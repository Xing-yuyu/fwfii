from fwfii.fc import *
from fwfii.utils import Delay
f1=Flight(1201)

ProgrammingMode(f1)
ProgrammingMode(f2)
ProgrammingMode(f3)
ProgrammingMode(f4)
ProgrammingMode(f5)
ProgrammingMode(f6)
ProgrammingMode(f7)
ProgrammingMode(f8)
ProgrammingMode(f9)
Delay(2000)
MaxVelXY(f1,200)
MaxAccXY(f1,200)
MaxVelZ(f1,200)
MaxAccZ(f1,200)
Arm(f1)
Delay(1000)
Takeoff(f1,100)
Delay(2000)
Move2(f1,60,20,100)
Delay(4000)
MaxVelZ(f1,60)
MaxAccZ(f1,50)
Land(f1)

Delay(1000)



