"""
三角编队飞行 — 三机统一离线脚本 (MultiPlan)
==============================================
一个 .py 文件编写三架无人机的完整飞行脚本 (ts + Delay 混用),
配合背景音乐完成编队表演。

无人机 (80cm 定位毯):
  - UAVID=98101  起始位置 (20, 20)  低空层 F1  80~120cm
  - UAVID=98102  起始位置 (60, 20)  中空层 F2  130~170cm
  - UAVID=98103  起始位置 (40, 60)  高空层 F3  180~220cm

安全规则:
  - 同一高度层 XY 间距 > 40cm
  - XY 间距 < 40cm 时 Z 差 >= 50cm
  - 三层分离: 低层(80-120) / 中层(130-170) / 高层(180-220)

航线:
  Phase 1 (0~3s):   解锁 + 闪烁
  Phase 2 (3~5s):   分层起飞
  Phase 3 (5~10s):  三角展开 + 绿色
  Phase 4 (10~15s): 交叉换位 + 蓝色
  Phase 5 (15~20s): 中心汇合 + 红色灯光秀
  Phase 6 (20~28s): 空中旋转 + 彩虹
  Phase 7 (28~35s): 降落 + 金色告别

音乐: 祖海 - 好运来 (music.mp3)

用法:
    # Step 1: 构建 (编译 + 拆分 + 项目结构)
    from fwfii import MultiPlan
    mp = MultiPlan()
    mp.add_drone(98101, pos=(20, 20))
    mp.add_drone(98102, pos=(60, 20))
    mp.add_drone(98103, pos=(40, 60))
    mp.set_music("music.flac")
    mp.set_carpet(80)
    mp.build("triangle_formation.py", "./output")
"""
from fwfii import Flight, Arm, Disarm, Takeoff, Land, Move2, Delay
from fwfii import MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ
from fwfii import AllOn, AllOff, AllBlink, AllBreath, BodyOn, BodyBreath
from fwfii import MotorHorse
from fwfii import RED, GREEN, BLUE, YELLOW, CYAN, PURPLE, WHITE, ORANGE, PINK

# ── 三架无人机 ──
f1 = Flight(98101)  # 低空层
f2 = Flight(98102)  # 中空层
f3 = Flight(98103)  # 高空层

# ── 安全参数 ──
for f in (f1, f2, f3):
    MaxVelXY(f, 100)
    MaxVelZ(f, 60)
    MaxAccXY(f, 300)
    MaxAccZ(f, 300)

# ═══════════════════════════════════════════════
# Phase 1: 解锁 + 闪烁 (0s ~ 3s)
# ═══════════════════════════════════════════════
AllBlink(f1, RED,   300, 300, ts=0)
AllBlink(f2, GREEN, 300, 300, ts=0)
AllBlink(f3, BLUE,  300, 300, ts=0)
Arm(f1, ts=500)
Arm(f2, ts=500)
Arm(f3, ts=500)

Delay(2500)

# ═══════════════════════════════════════════════
# Phase 2: 分层起飞 (3s ~ 5s)
# ═══════════════════════════════════════════════
AllOn(f1, GREEN)
AllOn(f2, GREEN)
AllOn(f3, GREEN)
Takeoff(f1, 100)   # 低层
Takeoff(f2, 150)   # 中层
Takeoff(f3, 200)   # 高层
Delay(4000)

# ═══════════════════════════════════════════════
# Phase 3: 三角展开 (5s ~ 10s)
# ═══════════════════════════════════════════════
AllOn(f1, CYAN)
AllOn(f2, CYAN)
AllOn(f3, CYAN)
# F1→左前 (10,10)  F2→右前 (70,10)  F3→后方中心 (40,70)
Move2(f1, 10, 10, 100)
Move2(f2, 70, 10, 150)
Move2(f3, 40, 70, 200)
Delay(5000)

# ═══════════════════════════════════════════════
# Phase 4: 交叉换位 (10s ~ 15s)
# ═══════════════════════════════════════════════
AllOn(f1, PURPLE)
AllOn(f2, PURPLE)
AllOn(f3, PURPLE)
# F1→右上 (70,70)  F2→左下 (10,10)  F3→左中 (10,40)
# 安全: 三层高度分离，路径交叉安全
Move2(f1, 70, 70, 120)   # 低层升高 20cm
Move2(f2, 10, 10, 170)   # 中层升高 20cm
Move2(f3, 10, 40, 220)   # 高层保持
Delay(5000)

# ═══════════════════════════════════════════════
# Phase 5: 中心汇合 + 灯光秀 (15s ~ 20s)
# ═══════════════════════════════════════════════
# 精确卡点 15s: 红灯闪烁 → 蓝灯呼吸 → 绿灯常亮
AllBlink(f1, RED, 200, 200, ts=15000)
AllBlink(f2, RED, 200, 200, ts=15000)
AllBlink(f3, RED, 200, 200, ts=15000)

# 三机向中心汇聚 (保持 Z 差)
Move2(f1, 40, 40, 120, ts=15500)
Move2(f2, 40, 40, 170, ts=15500)
Move2(f3, 40, 40, 220, ts=15500)
Delay(2000)

# 灯光切换
AllBreath(f1, BLUE,  400, 400, ts=17500)
AllBreath(f2, GREEN, 400, 400, ts=17500)
AllBreath(f3, PURPLE,400, 400, ts=17500)
Delay(2500)

# ═══════════════════════════════════════════════
# Phase 6: 空中旋转 + 跑马灯 (20s ~ 28s)
# ═══════════════════════════════════════════════
# 三机向外散开
AllOn(f1, YELLOW)
AllOn(f2, ORANGE)
AllOn(f3, PINK)
Move2(f1, 20, 20, 100, ts=20000)
Move2(f2, 60, 20, 150, ts=20000)
Move2(f3, 40, 70, 200, ts=20000)
Delay(3000)

# 跑马灯 + 圆形运动
MotorHorse(f1, [RED, YELLOW, GREEN, CYAN],   True,  800, ts=23000)
MotorHorse(f2, [BLUE, PURPLE, PINK, WHITE],  False, 800, ts=23000)
MotorHorse(f3, [RED, WHITE, BLUE, YELLOW],   True,  800, ts=23000)

# F1 圆运动
Move2(f1, 40, 20, 100, ts=23300)
Move2(f1, 60, 40, 100, ts=24000)
Move2(f1, 40, 60, 100, ts=24700)
Move2(f1, 20, 40, 100, ts=25400)
Move2(f1, 40, 20, 100, ts=26100)

# F2 外圆运动 (反向)
Move2(f2, 40, 60, 150, ts=23300)
Move2(f2, 20, 40, 150, ts=24000)
Move2(f2, 40, 20, 150, ts=24700)
Move2(f2, 60, 40, 150, ts=25400)
Move2(f2, 40, 60, 150, ts=26100)

# F3 高空悬停观察
BodyBreath(f3, WHITE, 500, 500, ts=23000)
Move2(f3, 40, 40, 210, ts=24000)
Move2(f3, 40, 40, 200, ts=26100)
Delay(2500)

# ═══════════════════════════════════════════════
# Phase 7: 集合 + 降落 (28s ~ 35s)
# ═══════════════════════════════════════════════
# 回到起始位置
AllOn(f1, GREEN, ts=28500)
AllOn(f2, GREEN, ts=28500)
AllOn(f3, GREEN, ts=28500)
BodyBreath(f1, YELLOW, 1000, 1000, ts=28500)
BodyBreath(f2, YELLOW, 1000, 1000, ts=28500)
BodyBreath(f3, YELLOW, 1000, 1000, ts=28500)

Move2(f1, 20, 20, 100, ts=29000)
Move2(f2, 60, 20, 150, ts=29000)
Move2(f3, 40, 60, 200, ts=29000)
Delay(3000)

# 降落
AllBlink(f1, YELLOW, 300, 300)
AllBlink(f2, YELLOW, 300, 300)
AllBlink(f3, YELLOW, 300, 300)
Land(f1, ts=33000)
Land(f2, ts=33000)
Land(f3, ts=33000)
Delay(5000)

# 上锁
AllOff(f1, ts=38500)
AllOff(f2, ts=38500)
AllOff(f3, ts=38500)
Disarm(f1, ts=39000)
Disarm(f2, ts=39000)
Disarm(f3, ts=39000)
