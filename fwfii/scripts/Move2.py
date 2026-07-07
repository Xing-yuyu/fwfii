#!/usr/bin/env python

from fwfii.fc import *
from fwfii.utils import Delay

HeartBeat.Disable()

f1 = Flight(1001)


ProgrammingMode(f1)

Delay(2000)

Arm(f1)

Delay(2000)


# Take off to 100cm
Takeoff(f1,150)

# After take off, after 5s
Delay(5000)

Move2(f1, 200, 200, 150)

Delay(5000)

Move2(f1, 300, 100, 150)

Delay(5000)

Move2(f1, 300, 300, 150)
Delay(5000)

Move2(f1, 100, 300, 150)
Delay(5000)

# Land
Land(f1)

# after 2s
Delay(5000)

# Disarm
Disarm(f1)

# after 2s
Delay(2000)

Stop(f1)
