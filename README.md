# fwfii

`fwfii` is a low-level Python SDK for Fii F400/F600 educational drones. It
preserves the legacy wire protocol while adding testable runtime, transport,
mission-generation, and upload surfaces.

Status: software-tested on this host with mocks and loopback servers.
Real hardware is not verified by this repository work.

## Safety

Do not run hardware examples around powered propellers. The test suite never
contacts drone IP addresses, scans serial ports, sends broadcast packets, or
uploads to real hardware. Examples that can command hardware require an explicit
`--hardware` flag.

## Install

```bash
python -m pip install -e .
python -m pip install -e ".[dev]"
```

Optional extras:

```bash
python -m pip install -e ".[serial]"
python -m pip install -e ".[monitor]"
```

Supported Python metadata currently declares Python 3.9 and newer. CI tests
Python 3.10 and 3.12 on Ubuntu, Windows, and macOS.

## Core Runtime

Use one runtime to own queue dispatch, transport lifecycle, heartbeat, and
shutdown:

```python
from fwfii import FiiRuntime, MockTransport
from fwfii.fc import Arm

with FiiRuntime(transport=MockTransport()) as runtime:
    flight = runtime.add_flight(71101)
    Arm(flight)
```

`MockTransport` records packets and is the default for tests. `TcpTransport` and
`SerialTransport` are available for explicit hardware-facing configuration.

## Network Transport

Drone IDs map to IP addresses as:

```text
uav_id = group * 1000 + address
ip = 192.168.group.address
```

For tests and custom networks, provide host overrides:

```python
from fwfii import FiiRuntime, TcpTransport, TcpTransportConfig

transport = TcpTransport(
    TcpTransportConfig(
        command_port=10014,
        host_overrides={71101: "127.0.0.1"},
    )
)
```

Explicit configuration is preferred on machines with VPNs, Docker, WSL,
firewalls, or multiple network interfaces.

## Serial Transport

Serial support is optional and requires `fwfii[serial]`.

Example port names:

- Windows: `COM3`
- Linux: `/dev/ttyUSB0` or `/dev/ttyACM0`
- macOS: `/dev/cu.*`

On Linux, the user may need membership in the `dialout` group. RTS/CTS can be
enabled with `SerialTransport(..., rtscts=True)`.

## Offline Missions

Mission generation is deterministic and uses `pathlib.Path`:

```python
from fwfii.quick import plan

plan("examples/mission/mission.py", "./output")
```

Mission uploads use `MissionUploader` and report structured results:

```python
from fwfii.planning import MissionUploader

uploader = MissionUploader("127.0.0.1", port=10034)
results = uploader.upload_path("./output")
```

Tests upload only to loopback fake servers.

## Emergency Commands

Emergency commands enter the runtime queue with high priority. They no longer
depend on a forgotten local IPC server or print success when nothing received
the command. `FiiRuntime.emergency_stop()` returns a `TransportResult`.

```python
result = runtime.emergency_stop(flight)
if not result.success:
    raise RuntimeError(result.error)
```

## Compatibility

Common legacy imports remain available where practical:

```python
from fwfii import FiiRuntime
from fwfii.fc import Flight, Takeoff, Land, Move2
```

Legacy helpers such as `fwfii.quick.connect()` remain, but new code should prefer
`FiiRuntime` with explicit transports. Optional monitor dependencies are no
longer imported as part of the core `fwfii.fc` import path.

## Verification

Local software verification includes:

- package import smoke test;
- protocol size, CRC, and golden command packet tests;
- mission wrapper timestamp regression tests;
- deterministic one-flight and multi-flight `.ls` generation tests;
- loopback fake upload server test;
- mock runtime startup, emergency priority, failure reporting, and shutdown
  tests;
- loopback TCP transport and fake serial transport tests.

Hardware verification remains deferred.
