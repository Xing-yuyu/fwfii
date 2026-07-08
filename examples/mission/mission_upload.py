"""Offline mission upload example.

This script compiles locally, but upload/start require --hardware.
"""
import argparse

from fwfii.quick import connect, deliver, mission_start, plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", action="store_true")
    parser.add_argument("--uav-id", type=int, default=71101)
    parser.add_argument("--segment", type=int, default=71)
    args = parser.parse_args()

    plan("mission.py", "./output")
    if not args.hardware:
        print("Compiled mission only. Refusing upload/start without --hardware.")
        return

    deliver(args.uav_id, "./output")
    connect(args.uav_id)
    mission_start([args.segment], countdown=5)


if __name__ == "__main__":
    main()
