from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight, Arm, Takeoff, Land, Disarm
from fwfii.fc.advanced import SetFlightMode
from fwfii.utils import Delay
import time

# 1. 启动通信
print("启动通信...")
d = TcpDelivery(vo=None)
h = HeartBeat()

# 2. 等待连接建立
print("等待连接...")
time.sleep(3)

# 3. 创建 Flight
f1 = Flight(71101)

# 4. 先看当前位置
print(f"当前位置: {f1.position}")

# 5. 切换到 GUIDED 模式
print("切换 GUIDED 模式...")
SetFlightMode(f1, 4)
Delay(1000)

# 6. 解锁
print("解锁...")
Arm(f1)
Delay(2000)

# 7. 起飞到 100cm
print("起飞!")
Takeoff(f1, 100)
Delay(5000)

# 8. 查看位置
print(f"空中位置: {f1.position}")

# 9. 降落
print("降落...")
Land(f1)
Delay(5000)

# 10. 上锁
print("上锁...")
Disarm(f1)
Delay(2000)

h.close()
d.close()
print("完成!")