"""
电池 + 心跳输出模式测试
=======================
验证电池百分比读取，以及三种心跳输出模式。
"""
from fwfii.quick import connect, disconnect
from fwfii import set_beat_output
from fwfii.utils import Delay

DRONE_ID = 71101

# ==========================================
# 1. 连接（心跳默认 normal 模式）
# ==========================================
print("=" * 55)
print("  测试: 心跳输出模式")
print("=" * 55)
print(f"\n连接 {DRONE_ID} ...")
d, h, f1 = connect(DRONE_ID)

# 等待就绪
for _ in range(20):
    if f1.fcstatus != "N/A":
        break
    Delay(200)

bat = f1.voltage
print(f"\n电池: {bat}%  |  fcstatus: {f1.fcstatus}  |  mode: {f1.flightmode}")

# ==========================================
# 2. 测试 slow 模式 (1Hz)
# ==========================================
print(f"\n{'='*55}")
print("切换到 'slow' 模式 (1秒/次)")
print("观察 5 秒...")
set_beat_output("slow")
Delay(5000)

# ==========================================
# 3. 测试 off 模式
# ==========================================
print(f"\n{'='*55}")
print("切换到 'off' 模式 (静默)")
print("观察 3 秒 — 应无输出...")
set_beat_output("off")
Delay(3000)

# ==========================================
# 4. 恢复 normal 模式
# ==========================================
print(f"\n{'='*55}")
print("恢复 'normal' 模式")
set_beat_output("normal")
Delay(2000)

# ==========================================
# 5. 结束
# ==========================================
bat = f1.voltage
print(f"\n最终电池: {bat}%")
disconnect()
print("测试结束。")
