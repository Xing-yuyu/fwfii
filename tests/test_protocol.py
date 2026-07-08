import ctypes
from collections import namedtuple

from fwfii.atom import (
    AtomRepo,
    buzzerPayload,
    crc,
    flightPayload,
    lightPayload,
    uavPack,
    wifiPack,
    zigbeePack,
)
from fwfii.fc import (
    Arm,
    Disarm,
    Land,
    MissionContinue,
    MissionPause,
    MissionStart,
    Move2,
    MoveDelta,
    Stop,
    Takeoff,
)
from fwfii.utils import GetTimerPassMs, TimerStart


FlightRef = namedtuple("FlightRef", ["uavid"])


def queued_packet(command, *args):
    AtomRepo.clear()
    zigbeePack.COUNTER = 0
    command(*args)
    return AtomRepo.getNext(timeout=1)


def decode_wifi(packet):
    element = wifiPack.from_buffer_copy(packet.payload)
    payload = flightPayload.from_buffer_copy(element.payload)
    return element, payload


def test_protocol_ctypes_sizes_are_stable():
    assert ctypes.sizeof(wifiPack) == 32
    assert ctypes.sizeof(zigbeePack) == 40
    assert ctypes.sizeof(uavPack) == 22
    assert ctypes.sizeof(flightPayload) == 24
    assert ctypes.sizeof(lightPayload) == 6
    assert ctypes.sizeof(buzzerPayload) == 24


def test_crc_known_vector():
    assert crc(b"123456789") == 0xF4


def test_golden_command_packets():
    flight = FlightRef(71101)
    cases = [
        (Arm, (flight,), "dd2501806547d52100000000308000000000010000000000000000000000000000000000000000be"),
        (Disarm, (flight,), "dd2501806547d50d00000000308000000000000000000000000000000000000000000000000000ca"),
        (Takeoff, (flight, 120), "dd2501806547d51700000000328000780000000000000000000000000000000000000000000000e4"),
        (Land, (flight,), "dd2501806547d5f100000000318000000000010000000000000000000000000000000000000000c9"),
        (Stop, (flight,), "dd2501806547d5560000000033800000000001000000000000000000000000000000000000000027"),
        (Move2, (flight, 10, -20, 30), "dd2501806547d56f00000000108000b80b0030f8ffffe8030000000000000000000000000000006c"),
        (MoveDelta, (flight, 10, -20, 30), "dd2501806547d5bf00000000118000b80b0030f8ffffe8030000000000000000000000000000001b"),
    ]

    for command, args, expected_hex in cases:
        packet = queued_packet(command, *args)

        assert bytes(packet).hex() == expected_hex


def test_mission_wrappers_preserve_timestamp_and_command_fields():
    flight = FlightRef(71101)

    for wrapper, command in [
        (MissionStart, 0),
        (MissionContinue, 1),
        (MissionPause, 2),
    ]:
        packet = queued_packet(wrapper, flight, 1234)
        element, payload = decode_wifi(packet)

        assert element.pack_header.reg == 52
        assert element.pack_header.ts == 1234
        assert payload.x == command
        assert payload.y == 0
        assert payload.z == 0


def test_buzzer_payload_uses_on_off_argument():
    assert buzzerPayload(1, 440, 50, 1).on_off == 1
    assert buzzerPayload(1, 440, 50, 0).on_off == 0


def test_timer_start_resets_global_timer():
    TimerStart()

    assert 0 <= GetTimerPassMs() < 1000


def test_atom_repo_emergency_priority_precedes_normal_items():
    AtomRepo.clear()
    AtomRepo.storage("normal")
    AtomRepo.storage("emergency", priority=True)

    assert AtomRepo.getNext(timeout=1) == "emergency"
    assert AtomRepo.getNext(timeout=1) == "normal"
