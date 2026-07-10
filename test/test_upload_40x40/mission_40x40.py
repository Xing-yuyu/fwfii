"""
40×40 毯 — 上传模式飞行脚本 (单机 71101)
==========================================
由 plan() 编译成 .ls 再 deliver() 上传到无人机执行。

航线: 起飞 → 正方形 → 升高 → 降落
"""
from fwfii import Flight
from fwfii import Arm, Disarm, Takeoff, Land, Move2, Delay
from fwfii import MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ
from fwfii import AllOn, AllBlink, AllOff
from fwfii import RED, GREEN, BLUE, YELLOW, WHITE

f1 = Flight(71101)

# ── 安全参数 (40cm 小毯，低速) ──
MaxVelXY(f1, 50)
MaxVelZ(f1, 30)
MaxAccXY(f1, 200)
MaxAccZ(f1, 200)

# ── 解锁 ──
AllBlink(f1, BLUE, 300, 300, ts=0)
Arm(f1, ts=500)

# ── 起飞 → 80cm ──
Delay(2000)
AllOn(f1, GREEN)
Takeoff(f1, 80)
Delay(5000)

# ── 正方形航线 (15cm 步长) ──
AllOn(f1, WHITE)
Move2(f1, 30, 10, 80)
Delay(2500)

Move2(f1, 30, 30, 80)
Delay(2500)

Move2(f1, 10, 30, 80)
Delay(2500)

Move2(f1, 10, 10, 80)
Delay(2500)

# ── 中心升高 → 100cm ──
AllOn(f1, RED)
Move2(f1, 20, 20, 100)
Delay(3000)

# ── 下降 → 60cm ──
AllOn(f1, GREEN)
Move2(f1, 20, 20, 60)
Delay(2000)

# ── 降落 + 上锁 ──
AllBlink(f1, YELLOW, 300, 300)
Land(f1)
Delay(5000)

AllOff(f1)
Disarm(f1)
