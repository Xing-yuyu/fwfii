import threading
import time

from fwfii import FiiRuntime, RuntimeConfig
from fwfii.atom import wifiPack, zigbeePack
from fwfii.fc import Arm, Disarm, ReadPosition2, Stop
from fwfii.transport import MockTransport


def wait_until(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def packet_reg(raw_packet):
    packet = zigbeePack.from_buffer_copy(raw_packet)
    element = wifiPack.from_buffer_copy(packet.payload)
    return element.pack_header.reg


def test_runtime_dispatches_multiple_flights_and_closes_cleanly():
    transport = MockTransport()
    runtime = FiiRuntime(transport=transport).start()
    f1 = runtime.add_flight(71101)
    f2 = runtime.add_flight(71102)

    Arm(f1)
    Disarm(f2)

    assert wait_until(lambda: len(transport.sent) == 2)
    assert [target for target, _ in transport.sent] == [71101, 71102]

    runtime.close()
    runtime.close()
    assert not runtime.is_running


def test_emergency_commands_are_dispatched_before_normal_queue_items():
    transport = MockTransport()
    runtime = FiiRuntime(transport=transport)
    flight = runtime.add_flight(71101)

    Arm(flight)
    Stop(flight, emergency=True)
    runtime.start()

    assert wait_until(lambda: len(transport.sent) == 2)
    runtime.close()

    assert [packet_reg(raw) for _, raw in transport.sent] == [51, 48]


def test_emergency_stop_reports_transport_failure():
    transport = MockTransport(fail_targets={71101})
    runtime = FiiRuntime(transport=transport).start()
    flight = runtime.add_flight(71101)

    result = runtime.emergency_stop(flight, timeout=1)

    runtime.close()
    assert not result.success
    assert result.target_uav == 71101
    assert "failure" in result.error


def test_heartbeat_does_not_require_appdata(monkeypatch):
    monkeypatch.delenv("APPDATA", raising=False)
    transport = MockTransport()
    runtime = FiiRuntime(
        transport=transport,
        config=RuntimeConfig(heartbeat=True, heartbeat_interval=0.01),
    ).start()
    flight = runtime.add_flight(71101)

    assert wait_until(lambda: len(transport.sent) >= 3)
    assert runtime._heartbeat.errors == []
    assert ReadPosition2(flight) == [0, 0, 0]

    runtime.close()


def test_runtime_shutdown_leaves_no_live_dispatcher_threads():
    runtime = FiiRuntime().start()
    runtime.close()

    assert not any(
        thread.name == "fwfii-dispatcher" and thread.is_alive()
        for thread in threading.enumerate()
    )
