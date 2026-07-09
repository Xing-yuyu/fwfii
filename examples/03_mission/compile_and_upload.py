"""
40×40 定位毯 — 上传模式测试 (71101)
=====================================
完整流程: plan(编译) → deliver(上传) → execute(执行)

前提:
    - 无人机 71101 已开机
    - 电脑已连 WiFi (192.168.71.x)
    - 无人机在 40×40 定位毯中心
"""
from fwfii.quick import connect, disconnect, plan, deliver
from fwfii.fc import Flight, Arm, Disarm
from fwfii.fc.advanced import SetFlightMode
from fwfii.fc import PlanningMode, MissionStart
from fwfii.utils import Delay
import time
import os
import sys

# ============ 配置 ============
DRONE_ID = 71101
MISSION_SCRIPT = os.path.join(os.path.dirname(__file__), "mission", "test_40x40_mission.py")
OUTPUT_DIR    = os.path.join(os.path.dirname(__file__), "mission", "output")

# ============================================================
# Step 1: plan — 编译 Python 脚本 → .ls 二进制文件
# ============================================================
def step_plan():
    print("=" * 50)
    print("  STEP 1: 编译 (plan)")
    print("=" * 50)
    print(f"  输入: {MISSION_SCRIPT}")
    print(f"  输出: {OUTPUT_DIR}/")

    # 清旧
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    plan(MISSION_SCRIPT, OUTPUT_DIR)

    ls_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.ls')]
    if not ls_files:
        print("\n[FAIL] 未生成 .ls 文件!")
        sys.exit(1)

    print(f"\n  生成 {len(ls_files)} 个文件:")
    for f in sorted(ls_files):
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"    {f}  ({size} bytes)")
    return ls_files

# ============================================================
# Step 2: deliver — WiFi 上传 .ls 到无人机
# ============================================================
def step_deliver():
    print()
    print("=" * 50)
    print("  STEP 2: 上传 (deliver)")
    print("=" * 50)
    print(f"  目标: 192.168.71.101:10034  (uavid={DRONE_ID})")

    deliver(DRONE_ID, OUTPUT_DIR, ip="192.168.71.101")
    print()

# ============================================================
# Step 3: execute — 连接 + 执行已上传的任务
# ============================================================
def step_execute():
    print("=" * 50)
    print("  STEP 3: 执行任务 (execute)")
    print("=" * 50)

    print("\n[连接]")
    d, h, f1 = connect(DRONE_ID)
    f1.position = (20, 20, 0, 0)

    try:
        print("[PlanningMode]")
        PlanningMode(f1)
        Delay(500)

        print("[MissionStart!] — 无人机自动执行")
        MissionStart(f1)

        # 监控 (脚本约 30s)
        for i in range(35):
            time.sleep(1)
            x, y, z, yaw = f1.position
            bat = f1.voltage
            print(f"  t={i+1:2d}s  Pos=({x:5.0f},{y:5.0f},{z:5.0f})  "
                  f"Bat={bat}%  [{f1.flightmode}]", flush=True)
            # 检查是否已自动上锁
            if f1.flightmode == "STABILIZE" and z < 10:
                print("  无人机已自动降落上锁")
                break

    except KeyboardInterrupt:
        print("\n[中断]")
        Disarm(f1)
    finally:
        disconnect()

# ============================================================
# 主入口
# ============================================================
def main():
    print("""
╔══════════════════════════════════════════════╗
║  fwfii 上传测试 — 40×40 毯 | 71101         ║
║                                            ║
║  1 = 完整流程 (plan→deliver→execute)       ║
║  2 = 仅编译   (plan)                       ║
║  3 = 仅上传   (deliver)                    ║
║  4 = 仅执行   (execute)                    ║
╚══════════════════════════════════════════════╝
""")

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = input("选模式 (1-4): ").strip()

    if mode in ('1',):
        step_plan()
        step_deliver()
        step_execute()
    elif mode in ('2',):
        step_plan()
    elif mode in ('3',):
        if not os.path.exists(OUTPUT_DIR) or not [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.ls')]:
            print("[INFO] output 为空, 先编译...")
            step_plan()
        step_deliver()
    elif mode in ('4',):
        step_execute()
    else:
        print(f"未知: {mode}")

    print("\n完成!")

if __name__ == "__main__":
    main()
