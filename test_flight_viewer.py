"""
40cm 毯飞行测试 — OpenCV 三视图实时监控
=========================================
pyfii 风格: 俯瞰(XY) + 前视(XZ) + 右视(YZ) + 状态栏
"""
from fwfii.quick import connect, disconnect
from fwfii import PositionViewer, set_beat_output
from fwfii import Arm, Takeoff, Land, Move2, Delay

DRONE_ID = 71101
CARPET = 40
FLY_ALT = 100

print("=" * 55)
print(f"  OpenCV 三视图 — {CARPET}cm 毯 — 无人机 {DRONE_ID}")
print("=" * 55)

print(f"\n连接 {DRONE_ID} ...")
d, h, f1 = connect(DRONE_ID)
f1.set_init_pos(0,0)
set_beat_output("normal")

viewer = PositionViewer(programmable=CARPET, scale=1.0)
viewer.start()
Delay(500)

print("\n解锁 + 起飞 ...")
Arm(f1)
Delay(1000)
Takeoff(f1, FLY_ALT)
Delay(4000)

print("飞正方形 (15cm步长) ...")
step = 40
Move2(f1, step, 0, FLY_ALT)
Delay(2000)
Move2(f1, step, step, FLY_ALT)
Delay(2000)
Move2(f1, 0, step, FLY_ALT)
Delay(2000)
Move2(f1, 0, 0, FLY_ALT)
Delay(2000)

print("降落 ...")
Land(f1)
Delay(4000)

print(f"\n最终位置: {f1.position}  电池: {f1.voltage}%")
"""viewer.stop()"""
disconnect()
print("测试结束。")
