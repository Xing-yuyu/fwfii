"""
测试: 单机上传模式 + 实时监控 — 40×40 毯
===========================================
plan(编译) → deliver(上传) → 连接 → 开监控 → 执行任务

用法:
    python test/test_upload_40x40.py              # 完整流程
    python test/test_upload_40x40.py plan         # 仅编译
    python test/test_upload_40x40.py upload       # 仅上传
    python test/test_upload_40x40.py fly          # 仅执行
"""
from fwfii.quick import connect, disconnect, plan, deliver
from fwfii import PositionViewer, set_beat_output
from fwfii import PlanningMode, MissionStart, Disarm
from fwfii.utils import Delay
import os
import sys
import time

# ============================================================
# 配置
# ============================================================
DRONE_ID  = 71101
DRONE_IP  = "192.168.71.101"
CARPET    = 40                     # 定位毯可编程尺寸
INIT_POS  = (20, 20)              # 无人机摆放位置 (毯子中心)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MISSION_PY = os.path.join(SCRIPT_DIR, "mission_40x40.py")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output_40x40")

# ============================================================
# Step 1: plan — 编译 .py → .ls
# ============================================================
def step_plan():
    print("=" * 55)
    print("  STEP 1: 编译 (plan)")
    print("=" * 55)
    print(f"  脚本: {MISSION_PY}")
    print(f"  输出: {OUTPUT_DIR}/")

    # 清空旧文件
    if os.path.exists(OUTPUT_DIR):
        for f in os.listdir(OUTPUT_DIR):
            os.remove(os.path.join(OUTPUT_DIR, f))
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    plan(MISSION_PY, OUTPUT_DIR)

    ls_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.ls')])
    if not ls_files:
        print("\n  [FAIL] 未生成 .ls 文件!")
        sys.exit(1)

    print(f"\n  生成 {len(ls_files)} 个 .ls 文件:")
    for f in ls_files:
        size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
        print(f"    {f}  ({size} bytes)")
    return True


# ============================================================
# Step 2: deliver — 上传 .ls 到无人机
# ============================================================
def step_deliver():
    print()
    print("=" * 55)
    print("  STEP 2: 上传 (deliver)")
    print("=" * 55)
    print(f"  目标: {DRONE_IP}:10034  (uavid={DRONE_ID})")

    if not os.path.isdir(OUTPUT_DIR) or not [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.ls')]:
        print("  [INFO] 无 .ls 文件，先编译...")
        step_plan()

    deliver(DRONE_ID, OUTPUT_DIR, ip=DRONE_IP)
    return True


# ============================================================
# Step 3: fly — 连接 + 预览 + 执行
# ============================================================
def step_fly():
    print()
    print("=" * 55)
    print("  STEP 3: 执行 + 实时监控")
    print("=" * 55)

    # 连接
    print(f"\n连接 {DRONE_ID} ...")
    d, h, f1 = connect(DRONE_ID)
    f1.set_init_pos(*INIT_POS)
    set_beat_output("slow")   # 控制台降频，主要看视图

    # 打开实时位置预览
    viewer = PositionViewer(programmable=CARPET, scale=1.0)
    viewer.start()
    Delay(500)

    try:
        # 进入上传模式
        print("\n[PlanningMode]")
        PlanningMode(f1)
        Delay(500)

        # 启动任务
        print("[MissionStart] → 无人机自动执行")
        MissionStart(f1)

        # 监控任务进度
        print("\n时间    X      Y      Z      电池  模式")
        print("-" * 55)
        start_t = time.time()
        while viewer.is_running:
            elapsed = time.time() - start_t
            x, y, z, yaw = f1.display_position
            bat = f1.voltage or 0
            print(f"{elapsed:4.0f}s   {x:5.0f}  {y:5.0f}  {z:5.0f}   "
                  f"{bat:3d}%  {f1.flightmode}", flush=True)

            # 检测任务结束 (降落上锁)
            if z <= 10 and f1.flightmode == "STABILIZE" and elapsed > 15:
                print("\n[检测到降落上锁] 任务完成")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[用户中断]")
        Disarm(f1)
    finally:
        viewer.stop()
        disconnect()

    elapsed = time.time() - start_t
    print(f"\n总飞行时间: {elapsed:.0f}s")
    return True


# ============================================================
# 主入口
# ============================================================
def main():
    print()
    print("╔" + "═" * 53 + "╗")
    print("║  fwfii 上传模式测试 — 40×40 毯 | 71101" + " " * 17 + "║")
    print("╠" + "═" * 53 + "╣")
    print("║  full  = 完整流程 (编译→上传→执行+监控)" + " " * 17 + "║")
    print("║  plan  = 仅编译" + " " * 35 + "║")
    print("║  upload= 仅上传" + " " * 35 + "║")
    print("║  fly   = 仅执行+监控" + " " * 31 + "║")
    print("╚" + "═" * 53 + "╝")
    print()

    mode = sys.argv[1] if len(sys.argv) > 1 else "full"

    if mode == "plan":
        step_plan()
    elif mode == "upload":
        step_deliver()
    elif mode == "fly":
        step_fly()
    else:  # full
        step_plan()
        step_deliver()
        step_fly()

    print("\n完成!")


if __name__ == "__main__":
    main()
