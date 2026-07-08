from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from .atom import AtomRepo
from .fc.flight import Flight
from .transport import MockTransport, TransportResult, packet_target_uavid

LOGGER = logging.getLogger(__name__)


@dataclass
class RuntimeConfig:
    heartbeat: bool = False
    heartbeat_interval: float = 0.2
    queue_timeout: float = 0.05
    shutdown_timeout: float = 2.0


class FiiRuntime:
    def __init__(self, transport=None, config: Optional[RuntimeConfig] = None):
        self.config = config or RuntimeConfig()
        self.transport = transport or MockTransport()
        self.flights: Dict[int, Flight] = {}
        self.results: List[TransportResult] = []
        self.errors: List[BaseException] = []
        self._results_lock = threading.Lock()
        self._stop = threading.Event()
        self._worker: Optional[threading.Thread] = None
        self._heartbeat = None
        self._closed = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    @property
    def is_running(self) -> bool:
        return self._worker is not None and self._worker.is_alive()

    def start(self):
        if self._closed:
            raise RuntimeError("runtime is closed")
        if self.is_running:
            return self
        self._stop.clear()
        self._worker = threading.Thread(target=self._dispatch, name="fwfii-dispatcher", daemon=True)
        self._worker.start()
        if self.config.heartbeat:
            from .fc.heartbeat import HeartBeat

            self._heartbeat = HeartBeat(interval=self.config.heartbeat_interval)
        return self

    def add_flight(self, uavid: int) -> Flight:
        if self._closed:
            raise RuntimeError("runtime is closed")
        flight = Flight(uavid)
        self.flights[uavid] = flight
        return flight

    def emergency_stop(self, flight: Flight, timeout: float = 2.0) -> TransportResult:
        if not self.is_running:
            raise RuntimeError("runtime must be started before sending emergency commands")
        start_index = len(self.results)
        from .fc import Stop

        Stop(flight, emergency=True)
        result = self.wait_for_result(packet_target=flight.uavid, start_index=start_index, timeout=timeout)
        if result is None:
            return TransportResult(False, flight.uavid, 0, "emergency command timed out")
        return result

    def wait_for_result(
        self,
        packet_target: Optional[int] = None,
        start_index: int = 0,
        timeout: float = 2.0,
    ) -> Optional[TransportResult]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._results_lock:
                candidates = self.results[start_index:]
                for result in candidates:
                    if packet_target is None or result.target_uav == packet_target:
                        return result
            time.sleep(0.01)
        return None

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._stop.set()
        if self._heartbeat is not None:
            self._heartbeat.close()
            self._heartbeat = None
        if self._worker is not None:
            self._worker.join(timeout=self.config.shutdown_timeout)
        for flight in list(self.flights.values()):
            try:
                from .fc.heartbeat import HeartBeat

                HeartBeat.removeFlight(flight)
            except Exception as exc:
                LOGGER.debug("failed to remove flight %s: %s", flight, exc)
        self.flights.clear()
        self.transport.close()

    def _dispatch(self):
        while not self._stop.is_set():
            try:
                packet = AtomRepo.getNext(timeout=self.config.queue_timeout)
            except AtomRepo.Empty:
                continue
            try:
                result = self.transport.send(packet)
            except Exception as exc:
                result = TransportResult(False, packet_target_uavid(packet), 0, str(exc))
                self.errors.append(exc)
                LOGGER.exception("transport send failed")
            with self._results_lock:
                self.results.append(result)
