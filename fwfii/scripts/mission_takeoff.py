from fwfii.fc import *
from fwfii.utils import Delay

f1 = Flight(1001)

ProgrammingMode(f1, emergency=True)
Delay(2000)
Arm(f1, emergency=True)
Delay(2000)
# Take off to 100cm
Takeoff(f1,150, emergency=True)
