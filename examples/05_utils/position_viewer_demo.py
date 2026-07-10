"""
位置实时监控 — OpenCV 三视图 (pyfii 风格)
==========================================
俯瞰(XY) + 前视(XZ) + 右视(YZ) + 状态栏

Esc 键退出查看器
"""
from fwfii.quick import connect, disconnect
from fwfii import PositionViewer, set_beat_output
import time

DRONE_ID = 71101
CARPET = 40   # 40/80/360/560

print("=" * 55)
print(f"  实时位置监控 — {CARPET}cm 可编程地毯")
print("=" * 55)

print(f"\n连接 {DRONE_ID} ...")
d, h, f1 = connect(DRONE_ID)
set_beat_output("off")

viewer = PositionViewer(programmable=CARPET, scale=1.0)
viewer.start()

print("\n三视图已打开 — 在地面移动无人机观察")
print("  Esc 键 或 Ctrl+C 退出\n")

try:
    while viewer.is_running:
        time.sleep(0.5)
except KeyboardInterrupt:
    pass

viewer.stop()
disconnect()
print("退出。")
