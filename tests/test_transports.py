import socket
import threading
from collections import namedtuple

from fwfii.atom import AtomRepo
from fwfii.fc import Arm
from fwfii.transport import SerialTransport, TcpTransport, TcpTransportConfig


FlightRef = namedtuple("FlightRef", ["uavid"])


def queued_arm_packet():
    Arm(FlightRef(71101))
    return AtomRepo.getNext(timeout=1)


def test_tcp_transport_sends_to_loopback_fake_server():
    received = bytearray()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def serve():
        try:
            conn, _addr = server.accept()
            with conn:
                received.extend(conn.recv(4096))
        finally:
            server.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()

    packet = queued_arm_packet()
    transport = TcpTransport(
        TcpTransportConfig(command_port=port, host_overrides={71101: "127.0.0.1"})
    )
    result = transport.send(packet)
    thread.join(timeout=1)

    assert result.success
    assert result.target_uav == 71101
    assert received == bytes(packet)


def test_serial_transport_uses_optional_fake_handle_and_closes():
    class FakeSerial:
        def __init__(self, **kwargs):
            self.kwargs = kwargs
            self.writes = []
            self.closed = False

        def write(self, payload):
            self.writes.append(payload)
            return len(payload)

        def close(self):
            self.closed = True

    fake = None

    def factory(**kwargs):
        nonlocal fake
        fake = FakeSerial(**kwargs)
        return fake

    packet = queued_arm_packet()
    transport = SerialTransport("loop://", serial_factory=factory, rtscts=True)
    result = transport.send(packet)

    transport.close()
    transport.close()

    assert result.success
    assert result.bytes_sent == len(bytes(packet))
    assert fake.kwargs["port"] == "loop://"
    assert fake.kwargs["rtscts"] is True
    assert fake.writes == [bytes(packet)]
    assert fake.closed is True
