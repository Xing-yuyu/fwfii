"""
最简飞行 - 起飞→悬停→降落
"""
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.utils import *

DRONE_ID = 71101
INIT_POS = (0, 0, 0, 0)

d, h, f1 = connect(DRONE_ID)
f1.position = INIT_POS

SetFlightMode(f1, 4)
Delay(500)
MaxVelXY(f1,200)
MaxVelZ(f1,200)
MaxAccZ(f1,400)
MaxAccXY(f1,400)
Arm(f1)
Delay(2000)
Takeoff(f1, 120)
Delay(3000)
"""Move2(f1,320,320,100)
Delay(5000)
Move2(f1,180,180,150)
Delay(5000)"""
"""Flip(f1,'x')
Delay(5000)
Flip(f1,'-x')
Delay(5000)"""
"""Move2(f1,40,40,100)
Delay(5000)
Land(f1)
Delay(5000)
Disarm(f1)"""

disconnect()