from __future__ import annotations

import socket
import struct
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Iterable, List, Optional

from fwfii.fc import Transfer


class UploadError(RuntimeError):
    pass


@dataclass(frozen=True)
class UploadResult:
    file: Path
    target: str
    port: int
    uavid: int
    bytes_sent: int
    checksum: int
    success: bool
    error: Optional[str] = None


def discover_mission_files(path) -> List[Path]:
    base = Path(path)
    if base.is_file():
        return [base]
    if not base.exists():
        raise UploadError("mission path does not exist: {}".format(base))
    if not base.is_dir():
        raise UploadError("mission path is not a file or directory: {}".format(base))
    return sorted(file for file in base.iterdir() if file.is_file() and file.suffix == ".ls")


def checksum_bytes(chunks: Iterable[bytes]) -> int:
    checksum = 0
    for chunk in chunks:
        checksum = (checksum + sum(bytearray(chunk))) & 0xFFFFFFFF
    return checksum


class MissionUploader:
    def __init__(self, host: str, port: int = 10034, timeout: float = 2.0, chunk_size: int = 512):
        if not host:
            raise UploadError("target host is required")
        self.host = host
        self.port = port
        self.timeout = timeout
        self.chunk_size = chunk_size

    def upload_file(self, file, uavid: int) -> UploadResult:
        path = Path(file)
        if not path.is_file():
            raise UploadError("mission file does not exist: {}".format(path))
        flight = SimpleNamespace(uavid=uavid)
        size = path.stat().st_size + 4
        checksum = 0
        bytes_sent = 0
        try:
            with socket.create_connection((self.host, self.port), timeout=self.timeout) as sock:
                sock.settimeout(self.timeout)
                start = bytes(Transfer(flight, 1, size, uavid))
                sock.sendall(start)
                bytes_sent += len(start)
                with path.open("rb") as handle:
                    while True:
                        chunk = handle.read(self.chunk_size)
                        if not chunk:
                            break
                        checksum = (checksum + sum(bytearray(chunk))) & 0xFFFFFFFF
                        sock.sendall(chunk)
                        bytes_sent += len(chunk)
                checksum_chunk = struct.pack("<I", checksum)
                sock.sendall(checksum_chunk)
                bytes_sent += len(checksum_chunk)
        except OSError as exc:
            return UploadResult(path, self.host, self.port, uavid, bytes_sent, checksum, False, str(exc))
        return UploadResult(path, self.host, self.port, uavid, bytes_sent, checksum, True)

    def upload_path(self, path, uavid: Optional[int] = None) -> List[UploadResult]:
        results = []
        for file in discover_mission_files(path):
            target_uav = uavid if uavid is not None else int(file.stem)
            results.append(self.upload_file(file, target_uav))
        return results
