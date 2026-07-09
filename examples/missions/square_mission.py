"""
40×40 定位毯任务 — plan() 编译用
================================
uavid: 71101  范围: XY 0~40cm Z ≤ 200cm

关键: 离线模式下必须用 ts (绝对毫秒时间戳)
     不能用 Delay() — Delay 不会写入 .ls 文件
"""
from fwfii.fc import Flight, Takeoff, Land, Move2, Arm, Disarm, MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ
from fwfii.led.lamp import AllOn, AllBlink, AllOff

DRONE_ID = 71101
f1 = Flight(DRONE_ID)

# =========== 时间轴 (ms) ===========
T0  = 0
T1  = 500          # 解锁
T2  = 2500         # 起飞
T3  = 7500         # → (30,10)
T4  = 10500        # → (30,30)
T5  = 13500        # → (10,30)
T6  = 16500        # → (10,10)
T7  = 19500        # → (20,20,100)
T8  = 22500        # → (20,20,60)
T9  = 24500        # 降落
T10 = 29500        # 上锁

# 基础参数 (ts 必须递增)
MaxVelXY(f1, 50, ts=T0)
MaxVelZ(f1, 30, ts=T0)
MaxAccXY(f1, 200, ts=T0)
MaxAccZ(f1, 200, ts=T0)

# 解锁
AllBlink(f1, 0x0000FF, 300, 300, ts=T0)
Arm(f1, ts=T1)

# 起飞 80cm
AllOn(f1, 0x00FF00, ts=T2)
Takeoff(f1, 80, ts=T2)

# 正方形航线
AllOn(f1, 0x0000FF, ts=T3)
Move2(f1, 30, 10, 80, ts=T3)

Move2(f1, 30, 30, 80, ts=T4)

Move2(f1, 10, 30, 80, ts=T5)

Move2(f1, 10, 10, 80, ts=T6)

# 中心升高 100cm
AllOn(f1, 0xFF0000, ts=T7)
Move2(f1, 20, 20, 100, ts=T7)

# 下降
AllOn(f1, 0x00FF00, ts=T8)
Move2(f1, 20, 20, 60, ts=T8)

# 降落
AllBlink(f1, 0xFFFF00, 300, 300, ts=T9)
Land(f1, ts=T9)

# 上锁
AllOff(f1, ts=T10)
Disarm(f1, ts=T10)
