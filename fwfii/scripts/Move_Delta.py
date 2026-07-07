#!/usr/bin/env python

from fwfii.fc import *
from fwfii.utils import Delay

f1 = Flight(1001)

ProgrammingMode(f1)

Delay(2000)

Arm(f1)

Delay(2000)


# Take off to 100cm
Takeoff(f1,150)

# After take off, after 5s
Delay(5000)

Forward(f1, 100)

Delay(5000)

Backward(f1, 100)
Delay(5000)

Left(f1, 100)
Delay(5000)

Right(f1, 100)
Delay(5000)

Yaw(f1, 9000)
Delay(2000)

Yaw(f1, 4500)
Delay(2000)

# Land
Land(f1)

# after 2s
Delay(5000)

# Disarm
Disarm(f1)

# after 2s
Delay(2000)

Stop(f1)

# after 2s
Delay(2000)




