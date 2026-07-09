"""
电池电压调试 - 查看 reg=8 原始响应字节
"""
from fwfii.quick import connect, disconnect
from fwfii.utils import Delay

DRONE_ID = 98101  # 改成你的飞机 ID

d, h, f1 = connect(DRONE_ID)

print("\n等待电池数据...（最多 15 秒）\n")

# 等待电压数据到达
for _ in range(30):
    if f1.voltage > 100:
        break
    Delay(500)

print(f"\n最终: voltage={f1.voltage} mV ({f1.voltage*0.001:.1f}V)")
print(f"fcstatus={f1.fcstatus}  flightmode={f1.flightmode}")

disconnect()
