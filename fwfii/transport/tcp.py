from __future__ import annotations

import socket
from dataclasses import dataclass, field
from typing import Dict

from .base import BaseTransport, TransportResult, packet_target_uavid


@dataclass
class TcpTransportConfig:
    command_port: int = 10014
    connect_timeout: float = 1.0
    host_overrides: Dict[int, str] = field(default_factory=dict)


class TcpTransport(BaseTransport):
    def __init__(self, config: TcpTransportConfig | None = None):
        self.config = config or TcpTransportConfig()
        self.closed = False

    def host_for_uavid(self, uavid: int) -> str:
        if uavid in self.config.host_overrides:
            return self.config.host_overrides[uavid]
        group = uavid // 1000
        address = uavid % 1000
        return "192.168.{}.{}".format(group, address)

    def send(self, packet) -> TransportResult:
        if self.closed:
            return TransportResult(False, packet_target_uavid(packet), 0, "transport is closed")
        target = packet_target_uavid(packet)
        if target is None:
            return TransportResult(False, None, 0, "packet has no target UAV")
        host = self.host_for_uavid(target)
        payload = bytes(packet)
        try:
            with socket.create_connection(
                (host, self.config.command_port),
                timeout=self.config.connect_timeout,
            ) as sock:
                sock.settimeout(self.config.connect_timeout)
                sock.sendall(payload)
        except OSError as exc:
            return TransportResult(False, target, 0, str(exc))
        return TransportResult(True, target, len(payload))

    def close(self) -> None:
        self.closed = True
