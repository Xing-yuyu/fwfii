"""
最简飞行示例 - 连接并起飞
前提：电脑已连上无人机 WiFi，无人机在定位毯上
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight, Arm, Takeoff, Land, Disarm
from fwfii.fc.advanced import SetFlightMode
from fwfii.utils import Delay
import time

# ==========================================
# 配置
# ==========================================
DRONE_ID = 71101            # 无人机 ID（IP: 192.168.71.101）
TAKEOFF_ALT = 100           # 起飞高度 (cm)
INIT_POSITION = (0, 0, 0, 0)  # 初始位置 (x, y, z, yaw)

# 1. 连接
print("连接无人机...")
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)

# 2. 创建无人机
f1 = Flight(DRONE_ID)
f1.position = INIT_POSITION

# 3. 飞行
SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)
Takeoff(f1, TAKEOFF_ALT)
Delay(5000)
Land(f1)
Delay(5000)
Disarm(f1)

h.close()
d.close()
print("完成！")