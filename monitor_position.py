from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight
from fwfii.utils import Delay
import time

# 连接
print("连接无人机...")
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)

f1 = Flight(71101)

print("\n=== 位置监控模式 ===")
print("在地面上手动挪动无人机，观察位置变化")
print("Ctrl+C 退出\n")

try:
    while True:
        x, y, z, yaw = f1.position
        print(f"X: {x:7.1f}  Y: {y:7.1f}  Z: {z:6.1f}  Yaw: {yaw:7.1f}", end='\r')
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\n\n退出")

h.close()
d.close()