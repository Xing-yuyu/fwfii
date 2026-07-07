from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight
from fwfii.atom import AtomRepo
from fwfii.utils import Delay
import time

# 1. 启动 TCP 通信
print("启动 TCP Delivery...")
d = TcpDelivery(vo=None)

# 2. 启动心跳
print("启动心跳...")
h = HeartBeat()

# 3. 创建 Flight
f1 = Flight(71101)

# 4. 等待连接
print("等待连接...")
time.sleep(5)

# 5. 检查
print(f"AtomRepo 队列: {AtomRepo.length()}")
print(f"连接的无人机: {list(d.server.keys())}")

# 6. 发送一条指令（心跳会自动发 HeartBeatData）
print("保持 5 秒...")
time.sleep(5)

print(f"AtomRepo 最终: {AtomRepo.length()}")

h.close()
d.close()