"""
无定位毯飞行 - 使用相对移动指令
注意：无定位毯时位置数据不准，建议低空慢速！
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight, Arm, Takeoff, Land, Disarm
from fwfii.fc.basic import Forward, Backward, Left, Right, Up, Down
from fwfii.fc.advanced import SetFlightMode
from fwfii.utils import Delay
import time

DRONE_ID = 71101
FLY_ALT = 80  # 飞行高度 (cm)，无定位毯建议 < 100cm

print("连接无人机...")
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)

f1 = Flight(DRONE_ID)
f1.position = (0, 0, 0, 0)

SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)

# 起飞
Takeoff(f1, FLY_ALT)
Delay(4000)

# 正方形航线
Forward(f1, 50)
Delay(3000)
Right(f1, 50)
Delay(3000)
Backward(f1, 50)
Delay(3000)
Left(f1, 50)
Delay(3000)

# 降落
Land(f1)
Delay(5000)
Disarm(f1)

h.close()
d.close()
print("完成！")