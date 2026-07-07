from fwfii.fc import *
from fwfii.utils import Delay

f1 = Flight(71101)

ProgrammingMode(f1, emergency=True)
Delay(4000)
Arm(f1, emergency=True)
Delay(4000)
# Take off to 100cm
Takeoff(f1,120, emergency=True)
Delay(3000)
Move2(f1,20,40,100,emergency=True)
Delay(3000)
Land(f1,emergency=True)
Delay(3000)
