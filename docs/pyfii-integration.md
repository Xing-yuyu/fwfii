# pyfii Backend Integration Notes

`fwfii` can serve as a future F400/F600 hardware backend for `pyfii` without
importing or modifying `pyfii` directly.

## Candidate Backend Shape

```python
backend.connect(uav_ids)
backend.compile(show)
backend.upload(compiled_show)
backend.start(...)
backend.stop(...)
backend.emergency_stop(...)
backend.read_status(...)
backend.close()
```

## Mapping Direction

- Choreography tracks map to timestamped F400/F600 movement and LED commands.
- Commands compile into per-UAV `.ls` files using the existing mission file
  layout.
- Upload uses `MissionUploader` with explicit target host, port, timeout, and
  result reporting.
- Synchronized launch maps to mission control commands such as `DelayLaunch`.
- Runtime status can be read from `Flight` state updated by heartbeat and
  transport receivers.

## Unresolved Protocol Questions

- Exact timestamp semantics for overlapping movement and LED commands.
- Movement interpolation expected by firmware.
- Whether LED and movement commands can overlap without firmware-side loss.
- Firmware limits for command count and `.ls` file size.
- Clock synchronization accuracy across multiple drones.
- Upload acknowledgment and retry behavior.
- Disconnect behavior during queued commands.
- Safe emergency-stop validation sequence on real hardware.

These questions require vendor documentation or controlled hardware testing.
