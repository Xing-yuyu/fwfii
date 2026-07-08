"""实时位置监控"""
from fwfii.quick import connect, disconnect
import time

DRONE_ID = 71101
d, h, f1 = connect(DRONE_ID)

print("X(cm)  Y(cm)  Z(cm)  Yaw(°)  模式  状态  电压(V)")
print("Ctrl+C 退出\n")

try:
    while True:
        x, y, z, yaw = f1.position
        print(f"X:{x:5.0f}  Y:{y:5.0f}  Z:{z:4.0f}  Yaw:{yaw/100:6.0f}°  "
              f"{f1.flightmode:8s}  {f1.fcstatus:12s}  {f1.voltage/1000:.1f}V", end='\r')
        time.sleep(0.3)
except KeyboardInterrupt:
    print("\n退出")

disconnect()