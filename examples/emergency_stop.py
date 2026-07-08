"""Emergency stop example.

This script does nothing unless --hardware is provided.
"""
import argparse

from fwfii import FiiRuntime, TcpTransport, TcpTransportConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", action="store_true")
    parser.add_argument("--uav-id", type=int, default=71101)
    parser.add_argument("--host")
    args = parser.parse_args()

    if not args.hardware:
        print("Refusing to send emergency command without --hardware.")
        return

    overrides = {args.uav_id: args.host} if args.host else {}
    transport = TcpTransport(TcpTransportConfig(host_overrides=overrides))
    with FiiRuntime(transport=transport) as runtime:
        flight = runtime.add_flight(args.uav_id)
        result = runtime.emergency_stop(flight)
        if not result.success:
            raise SystemExit("emergency command failed: {}".format(result.error))
        print("Emergency command sent to UAV {}".format(result.target_uav))


if __name__ == "__main__":
    main()
