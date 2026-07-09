"""
正方形任务 — ts + Delay 混用
===============================
uavid: 71101  范围: 40×40 定位毯

混用规则:
  - ts=xxx → 精确卡点 (灯光/音乐同步)
  - ts=0   → 自动从 plan() 开始计时
  - Delay() → 自然等待, 后续指令的时间戳自动累加

两种写法等价, 可随意混合:
  纯 ts:   Move2(f1, 30, 10, 80, ts=7500)
  纯 Delay: Delay(3000); Move2(f1, 30, 10, 80)
  混用:     AllOn(f1, RED, ts=9000); Delay(2000); Move2(...)
"""
from fwfii import Flight, Arm, Disarm, Takeoff, Land, Move2, Delay
from fwfii import MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ
from fwfii import AllOn, AllBlink, AllOff, GREEN, BLUE, RED, YELLOW

f1 = Flight(71101)

# ── 参数 ──
MaxVelXY(f1, 50)
MaxVelZ(f1, 30)
MaxAccXY(f1, 200)
MaxAccZ(f1, 200)

# ── 解锁 (精确卡点) ──
AllBlink(f1, BLUE, 300, 300, ts=0)
Arm(f1, ts=500)

# ── 起飞 ──
Delay(2000)
AllOn(f1, GREEN)
Takeoff(f1, 80)
Delay(5000)

# ── 正方形航线 ──
AllOn(f1, BLUE)
Move2(f1, 30, 10, 80)
Delay(3000)

Move2(f1, 30, 30, 80)
Delay(3000)

Move2(f1, 10, 30, 80)
Delay(3000)

Move2(f1, 10, 10, 80)
Delay(3000)

# ── 中心升高 (灯光精确卡第 22 秒) ──
AllOn(f1, RED, ts=22000)
Move2(f1, 20, 20, 100)
Delay(3000)

# ── 下降 ──
AllOn(f1, GREEN)
Move2(f1, 20, 20, 60)
Delay(2000)

# ── 降落 + 上锁 (精确卡点) ──
AllBlink(f1, YELLOW, 300, 300)
Land(f1, ts=30000)
Delay(5000)

AllOff(f1)
Disarm(f1, ts=36000)
