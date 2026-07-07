#!/usr/bin/env python

from fwfii.fc import *
from fwfii.utils import Delay

print('Start Running example.py script')

#
# Create a Flight 1 without mask
#

f1 = Flight(1001)

#
# Request Software Version
#

print('Request software version of Flight')
RequestVersion(f1)

#
# Request flight mode
#

print('Request flight mode of Flight')
RequestFlightMode(f1)

#
# Arm Flight 1
#

print('Arm the Flight')
ArmDisarm(f1, 1)

#
# Wait for 2 seconds
#
Delay(2000)

#
# Take off to 1m
#
Takeoff(f1, 100)

#
# Wait for 2 seconds
#
Delay(2000)

#
# Flight 1 moves to location(5, 3, 2)
#
print('Move the flight to (5, 3, 2)')
Displacement_Abs(f1, 5, 3, 2)

#
# Wait for 2 seconds
#
Delay(2000)

#
# Flight 1 Rotates Yaw 180 degree at location (5, 3, 2)
#
print('Rotate the flight to (0, 0, 18000)')
Rotation_Abs(f1, 0, 0, 18000)

#
# Wait for 2 seconds
#
Delay(2000)

#
# Flight 1 Lands at the current location
#
print('Landing')
Land(f1)

#
# Wait for 2 seconds
#
Delay(2000)

#
# Disarm
#
print('Disarm the Flight')
ArmDisarm(f1, 0)

#
# Wait for 2 seconds
#
Delay(2000)