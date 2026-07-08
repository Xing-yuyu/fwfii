from __future__ import annotations

from threading import Lock
from typing import Iterable, List, Set, Tuple

from .base import BaseTransport, TransportResult, packet_target_uavid


class MockTransport(BaseTransport):
    def __init__(self, fail_targets: Iterable[int] = ()):
        self.fail_targets: Set[int] = set(fail_targets)
        self.sent: List[Tuple[int, bytes]] = []
        self.closed = False
        self._lock = Lock()

    def send(self, packet) -> TransportResult:
        target = packet_target_uavid(packet)
        payload = bytes(packet)
        with self._lock:
            if self.closed:
                return TransportResult(False, target, 0, "transport is closed")
            if target in self.fail_targets:
                return TransportResult(False, target, 0, "mock transport failure")
            self.sent.append((target, payload))
        return TransportResult(True, target, len(payload))

    def close(self) -> None:
        with self._lock:
            self.closed = True
