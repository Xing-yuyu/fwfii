#!/usr/bin/env python
from gtrfs.fc import *
from gtrfs.utils import Delay

f1 = Flight(71101)#ip 192.168.1.1

Delay(2000)

Arm(f1)

Delay(1000)

# Take off to 100cm
Takeoff(f1,150)

# After take off, after 5s
Delay(5000)

# Land
Land(f1)

# after 2s
Delay(5000)

# Disarm
Disarm(f1,0,True)

# after 2s
Delay(2000)

#Stop(f1)

# after 2s
#Delay(2000)




