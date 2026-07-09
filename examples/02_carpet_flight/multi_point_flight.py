"""
多点变速飞行采集 — 1架无人机, 25个目标点, 不同速度
=====================================================
- 定位毯 360×360cm, 高度 40~200cm
- 每点间隔 5~10s（等飞机完全就位）
- 速度分 5 档随机分配
- 自动保存轨迹到 flight_logs/
=====================================================
"""
from fwfii.quick import connect, disconnect, start_log, stop_log
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.utils import *
import random

# ============================================
# 配置
# ============================================
DRONE_ID = 98101
INIT_POS = (40, 40, 0, 0)
SAVE_DIR = "./flight_logs"
ACC_XY = 400       # 水平加速度 cm/s²
ACC_Z  = 400       # 垂直加速度 cm/s²

# ============================================
# 目标点 — 覆盖整个定位毯 (x, y, z)
# ============================================
WAYPOINTS = [
    (40,   40,   80 ),    # 0  左下起
    (180,  40,   100),    # 1  底部中点
    (320,  40,   120),    # 2  右下
    (320,  180,  100),    # 3  右侧中点
    (320,  320,  80 ),    # 4  右上
    (180,  320,  120),    # 5  顶部中点
    (40,   320,  100),    # 6  左上
    (40,   180,  80 ),    # 7  左侧中点
    (180,  180,  60 ),    # 8  中心低
    (100,  100,  100),    # 9  左下区
    (260,  100,  100),    # 10 右下区
    (260,  260,  100),    # 11 右上区
    (100,  260,  100),    # 12 左上区
    (180,  180,  150),    # 13 中心中高
    (80,   80,   140),    # 14 左下高
    (280,  80,   140),    # 15 右下高
    (280,  280,  140),    # 16 右上高
    (80,   280,  140),    # 17 左上高
    (180,  180,  200),    # 18 中心最高
    (60,   180,  160),    # 19 左中
    (300,  180,  160),    # 20 右中
    (180,  60,   160),    # 21 下中
    (180,  300,  160),    # 22 上中
    (120,  120,  120),    # 23 内圈左下
    (240,  240,  120),    # 24 内圈右上
    (40,   40,   100),    # 25 回原点
]

# ============================================
# 速度档 — 每段飞行随机选一档
# ============================================
SPEED_PROFILES = [
    {"xy": 50,   "z": 30,  "name": "极慢"},
    {"xy": 80,   "z": 50,  "name": "慢速"},
    {"xy": 120,  "z": 80,  "name": "中速"},
    {"xy": 160,  "z": 100, "name": "快速"},
    {"xy": 200,  "z": 150, "name": "极速"},
]

# 每点停留时间范围（ms）
HOLD_MIN = 5000
HOLD_MAX = 10000


def main():
    print("=" * 55)
    print("  多点变速飞行采集")
    print(f"  目标点: {len(WAYPOINTS)} 个")
    print(f"  间隔:   {HOLD_MIN/1000:.0f}~{HOLD_MAX/1000:.0f}s/点")
    print(f"  范围:   360×360cm  |  高度 40~200cm")
    print("=" * 55)

    # 连接 + 记录
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS
    ProgrammingMode(f1)
    Delay(500)
    MaxAccXY(f1, ACC_XY); MaxAccZ(f1, ACC_Z)
    start_log(save_dir=SAVE_DIR, script_path=__file__)

    # 解锁 + 起飞
    print("\n[解锁]")
    Arm(f1)
    Delay(2000)

    print("[起飞 → 80cm]")
    Takeoff(f1, 80)
    Delay(5000)

    # 逐一飞目标点
    for i, (x, y, z) in enumerate(WAYPOINTS):
        # 随机选速度档
        sp = random.choice(SPEED_PROFILES)
        hold_ms = random.randint(HOLD_MIN, HOLD_MAX)

        print(f"\n[点 {i+1}/{len(WAYPOINTS)}] → ({x:3d},{y:3d},{z:3d})cm  "
              f"速度:{sp['name']}({sp['xy']}/{sp['z']}cm/s)  停留:{hold_ms/1000:.0f}s")

        # 设速度 → 移动 → 等到达
        MaxVelXY(f1, sp["xy"])
        MaxVelZ(f1, sp["z"])
        Move2(f1, x, y, z)
        Delay(hold_ms)

    # 降落
    print("\n[降落]")
    MaxVelXY(f1, 80)
    MaxVelZ(f1, 80)
    Land(f1)
    Delay(5000)
    Disarm(f1)

    # 保存
    stop_log()
    disconnect()
    print("\n" + "=" * 55)
    print("  飞行完成！数据在 flight_logs/ 目录")
    print("=" * 55)


if __name__ == "__main__":
    main()
