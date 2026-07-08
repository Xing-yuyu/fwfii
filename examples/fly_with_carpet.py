"""
定位毯飞行 - 正方形航线
"""
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.utils import *

DRONE_ID = 71101
INIT_POS = (0, 0, 0, 0)
ALT = 100

d, h, f1 = connect(DRONE_ID)
f1.position = INIT_POS

SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)
Takeoff(f1, ALT)
Delay(4000)

# 正方形
Forward(f1, 50); Delay(3000)
Right(f1, 50);  Delay(3000)
Backward(f1, 50); Delay(3000)
Left(f1, 50);   Delay(3000)

Land(f1); Delay(5000)
Disarm(f1)
disconnect()