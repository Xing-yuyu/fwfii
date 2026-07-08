from __future__ import annotations

from typing import Callable, Optional

from .base import BaseTransport, TransportResult, packet_target_uavid


class SerialTransport(BaseTransport):
    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 2.0,
        rtscts: bool = False,
        serial_factory: Optional[Callable] = None,
    ):
        if not port:
            raise ValueError("serial port is required")
        if serial_factory is None:
            try:
                import serial
            except ImportError as exc:
                raise ImportError(
                    "SerialTransport requires pyserial; install fwfii[serial]"
                ) from exc
            serial_factory = serial.Serial
        self.handle = serial_factory(port=port, baudrate=baudrate, timeout=timeout, rtscts=rtscts)
        self.closed = False

    def send(self, packet) -> TransportResult:
        target = packet_target_uavid(packet)
        if self.closed:
            return TransportResult(False, target, 0, "transport is closed")
        payload = bytes(packet)
        try:
            written = self.handle.write(payload)
        except OSError as exc:
            return TransportResult(False, target, 0, str(exc))
        return TransportResult(True, target, int(written if written is not None else len(payload)))

    def close(self) -> None:
        if not self.closed:
            self.closed = True
            self.handle.close()


def enumerate_serial_ports():
    try:
        from serial.tools import list_ports
    except ImportError as exc:
        raise ImportError("serial port discovery requires pyserial; install fwfii[serial]") from exc
    return [port.device for port in list_ports.comports()]
