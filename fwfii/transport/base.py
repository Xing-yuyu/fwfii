from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TransportResult:
    success: bool
    target_uav: Optional[int]
    bytes_sent: int = 0
    error: Optional[str] = None


def packet_target_uavid(packet) -> Optional[int]:
    header = getattr(packet, "zigbee_header", None)
    if header is None:
        return None
    return int(header.group) * 1000 + int(header.address)


class BaseTransport:
    def send(self, packet) -> TransportResult:
        raise NotImplementedError

    def close(self) -> None:
        pass
