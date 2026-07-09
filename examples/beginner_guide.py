"""
╔══════════════════════════════════════════════════════════════╗
║           fwfii 新手大全 — 从零到编队飞行                      ║
║                                                              ║
║  运行方式: 分段取消注释, 逐节学习                               ║
║  硬件需求: F400/F600 无人机 + 定位毯 + WiFi                     ║
║  修改配置: 改下面 DRONE_ID 为你的无人机 ID                       ║
╚══════════════════════════════════════════════════════════════╝

目录:
  第1节  连接 & 断开          第6节  LED 灯光系统
  第2节  解锁 & 上锁          第7节  遥测记录
  第3节  起飞 & 降落          第8节  多机编队
  第4节  移动 & 航线          第9节  离线任务(plan+deliver)
  第5节  速度 & 加速度        第10节 音乐 & 表演
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# ══════════════════════════════════════════════════════════════
# 全部可从顶层包一行导入
# ══════════════════════════════════════════════════════════════
from fwfii import (
    connect, disconnect, plan, deliver, mission_start,  # 快捷操作
    Flight,                                              # 无人机对象
    Arm, Disarm, Takeoff, Land, Move2, Hover,           # 飞行指令
    Forward, Backward, Left, Right, Up, Down,            # 相对移动
    Yaw, Flip,                                           # 旋转/特技
    MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ,               # 速度/加速度
    ProgrammingMode, PlanningMode,                       # 飞行模式
    MissionStart, MissionContinue, MissionPause,         # 任务控制
    Delay,                                                # 延时
    AllOn, AllOff, AllBlink, AllBreath,                  # LED 灯光
    BodyOn, BodyOff, BodyBlink, BodyBreath,
    MotorOn, MotorOff, MotorBlink, MotorBreath, MotorHorse,
    start_log, stop_log,                                 # 遥测记录
    load_music, play_music, stop_music, set_music_volume,# 音乐
    RED, GREEN, BLUE, YELLOW, CYAN, PURPLE, WHITE,       # 颜色
)

# ══════════════════════════════════════════════════════════════
# 配置 (改这里!)
# ══════════════════════════════════════════════════════════════
DRONE_ID = 71101       # 你的无人机 ID
INIT_POS = (20, 20, 0, 0)  # 定位毯上的初始 (x, y, z, yaw)


def section_1_connect():
    """第1节: 连接 & 断开 — 一切的前提"""
    print("=" * 50)
    print("第1节: 连接 & 断开")
    print("=" * 50)

    # connect() 做三件事:
    #   1. 启动 TcpDelivery (WiFi 通信, port 10014)
    #   2. 启动 HeartBeat   (心跳线程, 200ms 周期)
    #   3. 创建 Flight 对象  (代表你的无人机)
    # 返回值: (delivery, heartbeat, flight)
    d, h, f1 = connect(DRONE_ID)

    # 告诉无人机它在定位毯上的初始位置
    f1.position = INIT_POS

    # 查看当前状态
    x, y, z, yaw = f1.position
    print(f"位置: ({x:.0f}, {y:.0f}, {z:.0f}) cm")
    print(f"模式: {f1.flightmode}")
    print(f"状态: {f1.fcstatus}")

    # 断开 — 清理所有连接
    disconnect()
    print("已断开")


def section_2_arm():
    """第2节: 解锁 & 上锁 — 让电机转起来"""
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    # 必须先切换到编程模式
    ProgrammingMode(f1)
    Delay(500)

    # 解锁: 电机开始慢转 (注意安全!)
    Arm(f1)
    print("已解锁 — 电机转动中")
    Delay(3000)

    # 上锁: 电机停止
    Disarm(f1)
    print("已上锁")

    disconnect()


def section_3_takeoff():
    """第3节: 起飞 & 降落 — 飞起来!"""
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    ProgrammingMode(f1); Delay(500)
    Arm(f1); Delay(2000)

    # 起飞到 80cm — 慢慢升空
    print("起飞 → 80cm")
    Takeoff(f1, 80)
    Delay(5000)  # 悬停 5 秒

    # 降落
    print("降落")
    Land(f1)
    Delay(5000)

    Disarm(f1)
    disconnect()


def section_4_move():
    """第4节: 移动 & 航线 — 想去哪就去哪"""
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    ProgrammingMode(f1); Delay(500)
    Arm(f1); Delay(2000)

    # ── 起飞 ──
    Takeoff(f1, 60); Delay(4000)

    # ── 绝对坐标 — 飞到指定 (x, y, z) ──
    # 定位毯坐标系: x 右, y 前, z 上
    Move2(f1, 30, 30, 80)   # 飞到 (30, 30) 高度 80cm
    Delay(3000)

    Move2(f1, 10, 30, 80)   # 飞到 (10, 30)
    Delay(3000)

    Move2(f1, 10, 10, 80)   # 飞到 (10, 10)
    Delay(3000)

    # ── 相对移动 — 以当前位置为基准 ──
    Forward(f1, 20)    # 前进 20cm
    Delay(2000)
    Backward(f1, 10)   # 后退 10cm
    Delay(2000)
    Left(f1, 15)       # 左移 15cm
    Delay(2000)

    # ── 回到中心降落 ──
    Move2(f1, 20, 20, 60); Delay(2000)
    Land(f1); Delay(5000)
    Disarm(f1)
    disconnect()


def section_5_speed():
    """第5节: 速度 & 加速度 — 控制飞行姿态"""
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    ProgrammingMode(f1); Delay(500)

    # ── 速度限制 ──
    #   水平: 0 ~ 500 cm/s
    #   垂直: 0 ~ 300 cm/s
    MaxVelXY(f1, 150)   # 水平中速
    MaxVelZ(f1, 80)     # 垂直中速

    # ── 加速度限制 ──
    #   数值越大, 动作越"猛"
    MaxAccXY(f1, 300)   # 水平加速
    MaxAccZ(f1, 300)    # 垂直加速

    # ── 飞行 ──
    Arm(f1); Delay(2000)
    Takeoff(f1, 70); Delay(4000)

    # 高速飞对角线
    MaxVelXY(f1, 200)
    Move2(f1, 35, 35, 100); Delay(3000)

    # 低速回原点
    MaxVelXY(f1, 50)
    Move2(f1, 20, 20, 60); Delay(3000)

    Land(f1); Delay(5000)
    Disarm(f1)
    disconnect()


def section_6_led():
    """第6节: LED 灯光 — 让飞机亮起来"""
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    ProgrammingMode(f1); Delay(500)

    # ── 全灯 ──
    AllOn(f1, RED);       Delay(1000)    # 全红灯
    AllOn(f1, GREEN);     Delay(1000)    # 全绿灯
    AllOn(f1, BLUE);      Delay(1000)    # 全蓝灯
    AllOff(f1);           Delay(500)     # 灭灯

    # ── 闪烁 ──
    AllBlink(f1, YELLOW, 300, 300)       # 黄灯闪 (on 300ms / off 300ms)
    Delay(2000)
    AllOff(f1)

    # ── 呼吸 ──
    AllBreath(f1, PURPLE, 800, 800)      # 紫灯呼吸
    Delay(3000)
    AllOff(f1)

    # ── 机身灯 ──
    BodyOn(f1, CYAN);    Delay(1500)     # 机身青灯
    BodyBlink(f1, WHITE, 400, 400)       # 机身白闪
    Delay(2000)
    BodyOff(f1)

    # ── 电机灯 ──
    MotorOn(f1, 0, GREEN)                 # 四个电机全绿
    Delay(1500)
    MotorOff(f1, 0)

    # ── 跑马灯 ──
    MotorHorse(f1, [RED, GREEN, BLUE, YELLOW], True, 600)
    Delay(3000)
    AllOff(f1)

    disconnect()


def section_7_log():
    """第7节: 遥测记录 — 保存飞行数据到 CSV"""
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    # 开始记录 (自动保存遥测 CSV + 脚本副本)
    start_log(save_dir="./flight_logs", script_path=__file__)

    ProgrammingMode(f1); Delay(500)
    Arm(f1); Delay(2000)

    # 随便飞一段
    Takeoff(f1, 60); Delay(3000)
    Move2(f1, 30, 30, 80); Delay(3000)
    Move2(f1, 10, 10, 60); Delay(3000)
    Land(f1); Delay(5000)
    Disarm(f1)

    # 停止记录
    stop_log()
    # → flight_logs/flight_<时间戳>/
    #     ├── beginner_guide.py   (脚本副本)
    #     └── telemetry.csv       (时间,x,y,z,yaw,电量,状态)

    disconnect()


def section_8_swarm():
    """第8节: 多机编队 — 同时控制多架"""
    # 两架飞机必须在同一网段
    f1_id = 71101
    f2_id = 71102

    # 先连第一架
    d1, h1, f1 = connect(f1_id)
    f1.position = (10, 20, 0, 0)

    # 再连第二架 (共享 TcpDelivery + HeartBeat)
    d2, h2, f2 = connect(f2_id)
    f2.position = (30, 20, 0, 0)

    # 统一设置
    for f in (f1, f2):
        ProgrammingMode(f); Delay(300)

    # 统一解锁
    Arm(f1); Arm(f2); Delay(2000)

    # 分层起飞 (Z 差 ≥ 50cm 防止碰撞)
    Takeoff(f1, 60)    # 低空
    Takeoff(f2, 120)   # 高空
    Delay(4000)

    # 同步移动
    Move2(f1, 10, 30, 60)
    Move2(f2, 30, 30, 120)
    Delay(3000)

    # 同时降落
    Land(f1); Land(f2); Delay(5000)
    Disarm(f1); Disarm(f2)
    disconnect()


def section_9_mission():
    """第9节: 离线任务 — plan 编译 + deliver 上传 + 执飞

    ts + Delay 混用规则:
      - ts=xxx  → 精确卡点 (灯光/音乐同步)
      - Delay() → 自然等待, 后续指令时间戳自动累加
      - 两种写法可随意混用, plan() 自动处理
    """
    print("=" * 50)
    print("第9节: 离线任务 (ts + Delay 混用)")
    print("=" * 50)

    mission_code = '''
from fwfii import Flight, Arm, Disarm, Takeoff, Land, Move2, Delay
from fwfii import AllOn, AllOff, GREEN, BLUE, YELLOW

f1 = Flight({drone_id})

# 精确卡点
AllOn(f1, BLUE, ts=0)
Arm(f1, ts=500)

# 自然等待
Delay(2000)

# 自动 ts ≈ 2500
AllOn(f1, GREEN)
Takeoff(f1, 80)
Delay(5000)

# 航线 (自动累加时间戳)
Move2(f1, 30, 10, 80)
Delay(3000)
Move2(f1, 30, 30, 80)
Delay(3000)
Move2(f1, 10, 30, 80)
Delay(3000)
Move2(f1, 10, 10, 80)
Delay(3000)

# 精确卡点灯光 (第 22 秒)
AllOn(f1, YELLOW, ts=22000)
Move2(f1, 20, 20, 80)
Delay(3000)

Land(f1, ts=26000)
Delay(5000)

AllOff(f1)
Disarm(f1, ts=32000)
'''.format(drone_id=DRONE_ID)

    os.makedirs("missions", exist_ok=True)
    with open("missions/_tmp_mission.py", "w") as f:
        f.write(mission_code)

    # ── plan: 编译 .py → .ls ──
    print("[plan] 编译 (ts+Delay 混用)...")
    plan("missions/_tmp_mission.py", "./missions")

    # ── deliver: WiFi 上传 ──
    print("[deliver] 上传中...")
    deliver(DRONE_ID, "./missions")

    # ── 执飞 ──
    print("\n[execute] 连接无人机...")
    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    PlanningMode(f1); Delay(500)
    print("[MissionStart] 无人机自动执行!")
    MissionStart(f1)

    import time
    for i in range(40):
        time.sleep(1)
        x, y, z, _ = f1.position
        print(f"  t={i+1:2d}s  ({x:.0f},{y:.0f},{z:.0f})  [{f1.flightmode}]")

    disconnect()
    print("任务完成!")


def section_10_music():
    """第10节: 音乐播放 — 蜂群表演配乐"""
    import os

    d, h, f1 = connect(DRONE_ID)
    f1.position = INIT_POS

    # 加载音乐 (支持 .flac / .mp3 / .wav)
    music_file = "祖海 - 好运来.flac"
    if os.path.exists(music_file):
        load_music(music_file)
        set_music_volume(0.7)    # 70% 音量
        play_music(loops=0)      # 0=单次, -1=循环

        # 边飞边放音乐
        ProgrammingMode(f1); Delay(500)
        Arm(f1); Delay(2000)
        AllBreath(f1, GREEN, 600, 600)
        Takeoff(f1, 60); Delay(5000)
        Land(f1); Delay(5000)
        Disarm(f1)

        stop_music(fade_ms=2000)  # 淡出
    else:
        print(f"音乐文件 {music_file} 不存在, 跳过")

    disconnect()


# ══════════════════════════════════════════════════════════════
# 主入口 — 取消你想学的章节的注释
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import sys

    # 列出可用章节
    sections = {
        "1":  ("连接 & 断开",       section_1_connect),
        "2":  ("解锁 & 上锁",       section_2_arm),
        "3":  ("起飞 & 降落",       section_3_takeoff),
        "4":  ("移动 & 航线",       section_4_move),
        "5":  ("速度 & 加速度",     section_5_speed),
        "6":  ("LED 灯光",          section_6_led),
        "7":  ("遥测记录",          section_7_log),
        "8":  ("多机编队",          section_8_swarm),
        "9":  ("离线任务 plan+deliver", section_9_mission),
        "10": ("音乐播放",          section_10_music),
    }

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\n  fwfii 新手大全 — 选择章节:\n")
        for k, (name, _) in sections.items():
            print(f"    {k:>2}  {name}")
        print()
        choice = input("  输入编号 (1-10, 或 'all'): ").strip()

    if choice == "all":
        for name, func in sections.values():
            print(f"\n{'='*50}\n  运行: {name}\n{'='*50}")
            try:
                func()
            except KeyboardInterrupt:
                print("\n[中断] 跳到下一节")
            except Exception as e:
                print(f"\n[错误] {e} — 可能硬件未连接, 继续")
    elif choice in sections:
        name, func = sections[choice]
        try:
            func()
        except KeyboardInterrupt:
            print("\n[中断]")
    else:
        print(f"未知选择: {choice}")
