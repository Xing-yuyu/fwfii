"""
位置监控 - 实时查看无人机坐标（不起飞）
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight
import time

DRONE_ID = 98101

print("连接无人机...")
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)

f1 = Flight(DRONE_ID)

print("\n=== 位置监控 ===")
print("格式: X(cm)  Y(cm)  Z(cm)  Yaw(°)  模式  状态  电压(V)")
print("Ctrl+C 退出\n")

try:
    while True:
        x, y, z, yaw = f1.position
        yaw_deg = yaw / 100
        mode = f1.flightmode
        status = f1.fcstatus
        volt = f1.voltage / 1000

        print(f"X:{x:6.1f}  Y:{y:6.1f}  Z:{z:5.1f}  Yaw:{yaw_deg:7.1f}°  "
              f"{mode:10s}  {status:15s}  {volt:.2f}V", end='\r')
        time.sleep(0.3)
except KeyboardInterrupt:
    print("\n\n退出")

h.close()
d.close()