# fwfii Repository Audit

## Source Selection

The available working tree is `fwfii-dev-1` on Git branch `dev-1` from
`https://github.com/Xing-yuyu/fwfii.git`. The requested archive paths
`/mnt/data/fwfii-master.zip` and `/mnt/data/fwfii-dev-1.zip` are not present in
this environment, and a bounded search under `/media/kevin0412/Data` did not
find replacement archive files or extracted copies.

Because no `fwfii-master` source is available locally, this branch keeps
`fwfii-dev-1` as the maintained base and records that the master-vs-dev
comparison is blocked on missing source material.

## Baseline Verification

Commands run before code changes:

- `python -m compileall fwfii`: passed, with existing invalid-escape warnings.
- Package import smoke test: passed.
- `python -m pytest -q`: no tests existed, and default discovery imported the
  legacy example file `文档+示例脚本/testsocket.py`, which started network-facing
  code during collection.

`pytest.ini` now restricts test discovery to `tests/` so automated tests remain
offline and do not collect examples or vendor documentation scripts.

## Important Findings

- `setup.py` makes `pyserial` a hard runtime dependency, so importing/installing
  the core package is not cleanly separated from optional serial support.
- `fwfii.fc.__init__` imports monitor, odometry, obstacle, and detection modules
  at package import time, which can drag optional UI/scientific dependencies into
  core usage.
- `HeartBeat` writes position files under `os.getenv("APPDATA")`, which crashes
  outside Windows and performs filesystem writes on every heartbeat.
- `AtomRepo.getNext()` blocks indefinitely, which prevents clean dispatcher
  shutdown unless another command arrives.
- Legacy TCP/UDP/serial delivery threads are not consistently daemonized,
  joined, or closed; `TcpDelivery.close()` intentionally avoids joining workers.
- Emergency commands are sent through a local `multiprocessing.connection`
  listener and can print a connection failure while still returning success to
  callers.
- Mission wrappers call `Mission(flight, 0, ts, emergency)`, accidentally passing
  `ts` as `planid` and `emergency` as `missionid`.
- `buzzerPayload.__init__` assigns `self.on_off = self.on_off` instead of the
  caller-provided value.
- Path handling in mission upload uses backslash splitting and concatenation.
- `TimerStart()` assigns to a local `startT` instead of resetting the module
  timer.
- `TcpDelivery` calls an unavailable `Flight.setUTC()` method on launch-time
  responses.

## Safety Status

No real hardware verification has been performed. All changes in this branch
must keep tests offline, using mocks, local fake servers, loopback, or pure
packet generation.
