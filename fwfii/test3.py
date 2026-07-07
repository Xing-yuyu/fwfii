from fwfii.fc import *
from fwfii.fc.emergency import Emergency_Server
from fwfii.utils import *
from fwfii.led import *


s = Emergency_Server()
f1 = Flight(71101)

Delay(100)
MaxVelXY(f1,60,emergency=True)
MaxAccXY(f1,100,emergency=True)
MaxVelZ(f1,100,emergency=True)
MaxAccZ(f1,200,emergency=True)
Arm(f1)
Delay(1000)
Takeoff(f1,120,emergency=True)
Delay(3000)
Land(f1, emergency=True)
Delay(2000)


Delay(500)
s.close()
