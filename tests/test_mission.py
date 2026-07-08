import socket
import struct
import threading
import time
from collections import namedtuple

from fwfii.atom import flightPayload, wifiPack, zigbeePack
from fwfii.fc import Arm, GenLsEnd, Land
from fwfii.planning.deliver import scriptsGenerator
from fwfii.planning.uploader import MissionUploader, checksum_bytes, discover_mission_files


FlightRef = namedtuple("FlightRef", ["uavid"])


def wait_until(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def compile_ls(output_dir, commands):
    generator = scriptsGenerator(output_dir, append=False)
    generator.start()
    for command, args in commands:
        command(*args)
    GenLsEnd()
    assert wait_until(lambda: generator._end)
    generator.stop(timeout=1)
    generator.join(timeout=1)
    assert not generator.is_alive()
    return {file.name: file.read_bytes() for file in sorted(output_dir.glob("*.ls"))}


def test_one_flight_mission_generation_is_deterministic(tmp_path):
    flight = FlightRef(71101)
    commands = [(Arm, (flight, 100)), (Land, (flight, 200))]

    first = compile_ls(tmp_path / "first", commands)
    second = compile_ls(tmp_path / "second", commands)

    assert first == second
    assert list(first) == ["71101.ls"]
    assert first["71101.ls"].startswith(bytes(wifiPack(0, 0, 0, flightPayload(0, 0, 0, 0))))


def test_multi_flight_mission_generation_splits_files(tmp_path):
    f1 = FlightRef(71101)
    f2 = FlightRef(71102)

    files = compile_ls(tmp_path / "show", [(Arm, (f2, 100)), (Land, (f1, 200))])

    assert sorted(files) == ["71101.ls", "71102.ls"]
    assert files["71101.ls"] != files["71102.ls"]


def test_discover_mission_files_sorts_ls_files(tmp_path):
    (tmp_path / "71102.ls").write_bytes(b"b")
    (tmp_path / "notes.txt").write_text("ignore")
    (tmp_path / "71101.ls").write_bytes(b"a")

    assert [file.name for file in discover_mission_files(tmp_path)] == ["71101.ls", "71102.ls"]


def test_mission_uploader_sends_to_loopback_fake_server(tmp_path):
    mission = tmp_path / "71101.ls"
    payload = b"abc123"
    mission.write_bytes(payload)
    received = bytearray()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    def serve():
        try:
            conn, _addr = server.accept()
            with conn:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    received.extend(chunk)
        finally:
            server.close()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()

    result = MissionUploader("127.0.0.1", port=port, timeout=1).upload_file(mission, 71101)
    thread.join(timeout=1)

    assert result.success
    assert result.checksum == checksum_bytes([payload])
    assert received[40:-4] == payload
    assert struct.unpack("<I", received[-4:])[0] == checksum_bytes([payload])

    start_packet = zigbeePack.from_buffer_copy(received[:40])
    start_wifi = wifiPack.from_buffer_copy(start_packet.payload)
    start_payload = flightPayload.from_buffer_copy(start_wifi.payload)
    assert start_wifi.pack_header.reg == 53
    assert start_payload.x == 1
    assert start_payload.y == len(payload) + 4
    assert start_payload.z == 71101
