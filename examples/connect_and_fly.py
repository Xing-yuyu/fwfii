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
Arm(f1)
Delay(2000)
Takeoff(f1, 100)
Delay(5000)
Land(f1)
Delay(5000)
Disarm(f1)

disconnect()