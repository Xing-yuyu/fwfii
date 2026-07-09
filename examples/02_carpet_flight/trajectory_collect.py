"""
飞行轨迹采集程序
- 定位毯: 360×360cm
- 最大高度: 200cm
- 速度可调
- 飞行完成后自动保存 CSV + 脚本副本
"""
from fwfii.quick import connect, disconnect, start_log, stop_log
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.utils import *

# ============================================
# 配置区
# ============================================
DRONE_ID = 98101
INIT_POS = (0, 0, 0, 0)          # 起飞原点（定位毯左下角）
SAVE_DIR = "./flight_logs"        # 保存目录

# 速度档位（cm/s, cm/s²）
SPEED = {
    "slow":   (50,  30),    # (水平速度, 垂直速度)
    "medium": (100, 60),
    "fast":   (150, 200),
    "max":    (200, 400),
}
ACC_XY = 400   # 水平最大加速度 cm/s²
ACC_Z  = 400   # 垂直最大加速度 cm/s²

# ============================================
# 飞行航线定义
# ============================================

def fly_grid(f, h, step=80, alt=120):
    """
    网格扫描航线 — 覆盖 360×360 定位毯
    从原点出发，逐行扫描，适合采集均匀分布的数据
    """
    MaxAccXY(f, ACC_XY); MaxAccZ(f, ACC_Z)
    MaxVelXY(f, SPEED["medium"][0]); MaxVelZ(f, SPEED["medium"][1])

    # 起飞到巡航高度
    Takeoff(f, alt)
    WaitStable(3000)

    rows = 4  # 360/80 ≈ 4 行
    for row in range(rows):
        y_target = min(40 + row * step, 320)
        x_target = 320 if row % 2 == 0 else 40

        Move2(f, x_target, y_target, alt)
        WaitStable(2500)

    print("[Grid] 网格扫描完成")


def fly_spiral(f, h, center=(180, 180), alt=120):
    """
    螺旋航线 — 从中心向外螺旋
    适合测试不同半径下的定位精度
    """
    MaxAccXY(f, ACC_XY); MaxAccZ(f, ACC_Z)
    cur_speed = SPEED["slow"]

    Takeoff(f, alt)
    WaitStable(5000)

    # 飞到中心
    Move2(f, center[0], center[1], alt)
    WaitStable(5000)

    radii = [40, 80, 120, 160]
    for i, r in enumerate(radii):
        if i == 1:
            cur_speed = SPEED["medium"]
        elif i >= 2:
            cur_speed = SPEED["fast"]

        MaxVelXY(f, cur_speed[0])
        MaxVelZ(f, cur_speed[1])

        # 正方形螺旋: 四个角
        corners = [
            (center[0] + r, center[1] + r),   # 右上
            (center[0] - r, center[1] + r),   # 左上
            (center[0] - r, center[1] - r),   # 左下
            (center[0] + r, center[1] - r),   # 右下
        ]
        for cx, cy in corners:
            Move2(f, cx, cy, alt)
            WaitStable(5000)

    print("[Spiral] 螺旋航线完成")


def fly_z_stairs(f, h):
    """
    阶梯高度测试 — 在不同高度悬停
    测试 Z 轴定位精度
    """
    MaxAccXY(f, ACC_XY); MaxAccZ(f, ACC_Z)
    MaxVelXY(f, SPEED["slow"][0]); MaxVelZ(f, SPEED["slow"][1])

    Takeoff(f, 60)
    WaitStable(5000)

    heights = [80, 120, 160, 200]
    for z in heights:
        if z >= 160:
            MaxVelZ(f, SPEED["medium"][1])
        Move2(f, 180, 180, z)
        WaitStable(5000)

    print("[Z-Stairs] 阶梯高度测试完成")


def fly_rectangle(f, h, alt=100):
    """
    矩形航线 — 沿定位毯边缘飞行
    高速测试边界定位
    """
    MaxAccXY(f, ACC_XY); MaxAccZ(f, ACC_Z)
    MaxVelXY(f, SPEED["fast"][0]); MaxVelZ(f, SPEED["fast"][1])

    Takeoff(f, alt)
    WaitStable(5000)

    # 四个角，高速飞行
    corners = [
        (300, 300, alt),     # 右上角
        (40,  300, alt),     # 左上角
        (40,  40,  alt),     # 左下角
        (300, 40,  alt),     # 右下角
        (40,  40,  alt),     # 回到原点
    ]

    MaxVelXY(f, SPEED["fast"][0])
    for x, y, z in corners:
        Move2(f, x, y, z)
        WaitStable(5000)

    MaxVelXY(f, SPEED["slow"][0])  # 降速准备降落
    print("[Rectangle] 矩形航线完成")


def WaitStable(ms):
    """等待 + 留稳定时间"""
    Delay(ms)


# ============================================
# 主程序
# ============================================

def main():
    print("=" * 50)
    print("  飞行轨迹采集程序")
    print(f"  定位毯: 360×360cm  最大高度: 200cm")
    print("=" * 50)

    # 1. 连接 + 开始记录
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    # 启动数据记录（自动保存脚本副本 + 遥测 CSV）
    start_log(save_dir=SAVE_DIR, script_path=__file__)

    # 2. 设置编程模式
    ProgrammingMode(f1)
    Delay(500)

    # 3. 解锁
    MaxAccXY(f1, ACC_XY)
    MaxAccZ(f1, ACC_Z)
    Arm(f1)
    Delay(2000)
    print("\n[状态] 已解锁，开始飞行\n")

    # 4. 执行航线（根据需要选择/组合）
    try:
        # ---- 选择一条航线，或组合多条 ----

        fly_grid(f1, h)           # 网格扫描
        fly_spiral(f1, h)       # 螺旋航线
        fly_z_stairs(f1, h)     # 阶梯高度
        fly_rectangle(f1, h)    # 矩形高速

        # ---- 自定义航线示例 ----
        # MaxVelXY(f1, 150); MaxVelZ(f1, 80)
        # Takeoff(f1, 100); WaitStable(3000)
        # Move2(f1, 180, 180, 100); WaitStable(3000)
        # Move2(f1, 180, 180, 150); WaitStable(3000)

    except KeyboardInterrupt:
        print("\n[中断] 用户取消，立即降落")

    # 5. 降落 + 上锁
    print("\n[状态] 航线完成，开始降落...")
    MaxVelXY(f1, SPEED["slow"][0])
    MaxVelZ(f1, SPEED["slow"][1])
    Delay(5000)
    Land(f1)
    Delay(5000)
    Disarm(f1)

    # 6. 停止记录 + 断开
    stop_log()
    disconnect()

    print("\n" + "=" * 50)
    print("  飞行完成！数据已保存到:")
    print(f"  {SAVE_DIR}/flight_xxxxxx/")
    print("  ├── trajectory_collect.py  (飞行脚本)")
    print("  └── telemetry.csv          (遥测数据)")
    print("=" * 50)


if __name__ == "__main__":
    main()
