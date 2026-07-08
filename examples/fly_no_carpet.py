"""
无定位毯飞行 - 低空慢速相对移动
注意：高度建议 < 100cm
"""
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.basic import Forward, Backward, Left, Right
from fwfii.utils import *

DRONE_ID = 71101

d, h, f1 = connect(DRONE_ID)
f1.position = (0, 0, 0, 0)

SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)
Takeoff(f1, 80)
Delay(4000)

Forward(f1, 30); Delay(3000)
Backward(f1, 30); Delay(3000)
Left(f1, 30); Delay(3000)
Right(f1, 30); Delay(3000)

Land(f1); Delay(5000)
Disarm(f1)
disconnect()