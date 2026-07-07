#!/usr/bin/env python

from fwfii.fc import *

f1 = Flight(1001)


ProgrammingMode(f1)
Delay(3000)

Arm(f1)
Delay(2000)

Takeoff(f1, 150)
Delay(5000)

Move2(f1, 300, 200, 150)
Delay(5000)
#MovewHeading(f1, '-y', 200, True, 120)
#Delay(5000)

MaxAccXY(f1, 500)
MaxVelXY(f1, 500)
MaxAccZ(f1, 500)
MaxVelZ(f1, 300)
#Delay(2000)

SimpleHarmonic(f1, "y", 300, 200, 150, 50, 360, 1, 2)
#nod(f1, '-y', 30)
#Yaw(f1, 'l', 45)
#Delay(3000)
#Yaw2(f1, 'r', 90)
#Delay(3000)
#Yaw2(f1, 'r', 90)
Delay(3000)
Land(f1)

Delay(20)