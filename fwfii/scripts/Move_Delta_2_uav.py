#!/usr/bin/env python

from fwfii.fc import *
from fwfii.utils import Delay

f1 = Flight(1001)
f2 = Flight(1002)

ProgrammingMode(f1)
ProgrammingMode(f2)

Delay(2000)

Arm(f1)
Arm(f2)

Delay(2000)

# Take off to 100cm
Takeoff(f1,100)
Takeoff(f2,100)

# After take off, after 5s
Delay(5000)

Forward(f1, 100)
Forward(f2, 100)

# after 2s
Delay(5000)

Backward(f1, 100)
Backward(f2, 100)

# after 2s
Delay(5000)

Yaw(f1, 9000)
Yaw(f2, 9000)
Delay(2000)

# Land
Land(f1)
Land(f2)

# after 2s
Delay(5000)

# Disarm
Disarm(f1)
Disarm(f2)
# after 2s
Delay(2000)

Stop(f1)
Stop(f2)
Delay(2000)