"""
定位毯精确飞行 - 使用绝对坐标 Move2
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight, Arm, Takeoff, Land, Disarm, Move2
from fwfii.fc.advanced import SetFlightMode
from fwfii.utils import Delay
import time

DRONE_ID = 71101

# 定位毯上的初始位置（根据实际摆放修改）
INIT_X, INIT_Y, INIT_Z = 0, 0, 0

# 飞行目标点
TARGETS = [
    (INIT_X + 30, INIT_Y, 100),  # 前 30cm
    (INIT_X + 30, INIT_Y + 30, 100),  # 右 30cm
    (INIT_X, INIT_Y + 30, 100),  # 后 30cm
    (INIT_X, INIT_Y, 100),  # 回原点
]

print("连接无人机...")
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)

f1 = Flight(DRONE_ID)
f1.position = (INIT_X, INIT_Y, INIT_Z, 0)

SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)

# 起飞
Takeoff(f1, 100)
Delay(4000)

# 按目标点飞行
for i, (x, y, z) in enumerate(TARGETS):
    print(f"飞向目标 {i + 1}: ({x}, {y}, {z})")
    Move2(f1, x, y, z)
    Delay(4000)

    # 显示实际到达位置
    actual = f1.position
    print(f"  实际位置: ({actual[0]:.1f}, {actual[1]:.1f}, {actual[2]:.1f})")

# 降落
Land(f1)
Delay(5000)
Disarm(f1)

h.close()
d.close()
print("完成！")