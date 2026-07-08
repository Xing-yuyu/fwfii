"""Minimal hardware flight example.

This script does nothing unless --hardware is provided.
"""
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hardware", action="store_true")
    parser.add_argument("--uav-id", type=int, default=71101)
    args = parser.parse_args()

    if not args.hardware:
        print("Refusing to fly without --hardware.")
        return

    from fwfii.fc import Arm, Disarm, Land, SetFlightMode, Takeoff
    from fwfii.quick import connect, disconnect
    from fwfii.utils import Delay

    _delivery, _heartbeat, flight = connect(args.uav_id)
    flight.position = (0, 0, 0, 0)
    SetFlightMode(flight, 4)
    Delay(500)
    Arm(flight)
    Delay(2000)
    Takeoff(flight, 100)
    Delay(5000)
    Land(flight)
    Delay(5000)
    Disarm(flight)
    disconnect(args.uav_id)


if __name__ == "__main__":
    main()
