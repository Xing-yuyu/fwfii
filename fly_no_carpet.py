from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight, Arm, Takeoff, Land, Disarm, Stop
from fwfii.fc.basic import Forward, Backward, Left, Right, Up, Down, Hover
from fwfii.fc.advanced import SetFlightMode
from fwfii.utils import Delay
import time

# ==========================================
# 坐标初始化（无定位毯时手动输入估计位置）
# ==========================================
INIT_POSITION = (0, 0, 0, 0)

# 1. 连接
print("连接无人机...")
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)

# 2. 创建无人机
f1 = Flight(71101)
f1.position = INIT_POSITION

# 3. 切换到 GUIDED 模式（无定位毯也能用）
print("切换 GUIDED 模式...")
SetFlightMode(f1, 4)
Delay(500)

# 4. 解锁
print("解锁...")
Arm(f1)
Delay(2000)

# 5. 起飞到 100cm
print("起飞!")
Takeoff(f1, 100)
Delay(5000)

# 6. 前进 50cm（相对移动）
print("前进 50cm...")
Forward(f1, 20)
Delay(3000)

# 7. 后退 50cm
print("后退...")
Backward(f1, 20)
Delay(3000)

# 8. 左移 30cm
print("左移...")
Left(f1, 20)
Delay(3000)

# 9. 右移 30cm
print("右移...")
Right(f1, 20)
Delay(3000)

# 10. 上升 30cm
print("上升...")
Up(f1, 20)
Delay(2000)

# 11. 下降 30cm
print("下降...")
Down(f1, 20)
Delay(2000)

# 12. 降落
print("降落...")
Land(f1)
Delay(5000)

# 13. 上锁
Disarm(f1)
Delay(1000)

h.close()
d.close()
print("完成！")