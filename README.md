# fwfii — Fii Drone Flight Control SDK

Python 飞行控制库，适用于小鸟飞飞 (Fii) F400/F600 教育无人机。**完全脱离原版图形化软件**，纯 Python 控制。

## 项目结构

```
fwfii/
├── __init__.py              # 顶层包，一键导出所有 API
├── quick.py                 # 快捷操作: connect / disconnect / plan / deliver
├── swarm.py                 # 蜂群项目: SwarmProject 批量管理多机
├── offline_multi.py         # ★ 离线多机: MultiPlan 统一脚本 → 自动拆分
├── gtrfs_compat.py          # gtrfs 兼容层
├── fii_exporter.py          # ★ .fii 项目导出: 生成官方炫舞软件项目文件
│
├── fc/                      # 飞行控制核心
│   ├── flight.py            # Flight 对象 (位置/状态/电量)
│   ├── basic.py             # 高层指令: Arm, Takeoff, Move2, Flip, ...
│   ├── advanced.py          # 底层指令: wifiPack/zigbeePack 编码
│   ├── heartbeat.py         # 心跳线程 (200ms 轮询)
│   ├── position_viewer.py   # OpenCV 三视图 (XY/XZ/YZ) 实时定位
│   ├── monitor.py           # Curses/Matplotlib 多机仪表盘
│   ├── emergency.py         # 紧急停机通道
│   ├── detect.py            # 检测工具
│   ├── obstacle.py          # 避障
│   └── odom.py              # 里程计
│
├── led/                     # LED 灯光系统
│   └── lamp.py              # AllOn/BodyBlink/MotorHorse 等
│
├── atom/                    # 原子通信层
│   ├── delivery.py          # TcpDelivery (WiFi) / UdpDelivery / AtomDelivery (串口)
│   ├── gen.py               # 二进制包结构: wifiPack, zigbeePack, CRC
│   └── repo.py              # AtomRepo: 线程安全命令队列
│
├── planning/                # 离线任务编译
│   ├── deliver.py           # scriptsGenerator: 录制指令 → .ls 文件
│   └── conn.py              # 网络传输工具 (组播/广播/单播)
│
├── utils/                   # 工具
│   ├── utils.py             # Delay, GetCurMs, GetCurTime
│   ├── logger.py            # FlightLogger: 遥测 CSV 记录
│   └── music.py             # MusicPlayer: 背景音乐 (pygame)
│
├── core/                    # 核心工具
│   ├── planning_gen.py      # plan() 命令行入口
│   ├── planning_deliver.py  # deliver 命令行入口
│   ├── program_sock.py      # WiFi 编程工具
│   ├── program_uart.py      # 串口编程工具
│   └── ota.py               # OTA 固件升级
│
├── lightshow/               # 灯光秀 (图像/拓扑/屏幕映射)
│   ├── image.py, light.py, screen.py, topo.py
│
└── scripts/                 # 独立工具脚本 (Arm/Disarm/Takeoff/Mission/...)

examples/
├── beginner_guide.py        # ★ 新手大全: 10 节交互式教程
├── 01_basics/               # 基础操作
├── 02_carpet_flight/        # 定位毯航线
├── 03_mission/              # 离线任务完整流程
├── 04_swarm/                # 蜂群编队舞蹈
├── 05_utils/                # 工具 (电池/定位预览)
├── 06_offline_multi/        # ★ 离线多机: 统一脚本 → 自动拆分
└── missions/                # 任务脚本 (给 plan 编译用)

test/
├── test_offline_multi/      # MultiPlan 测试套件 (44 项)
├── test_upload_40x40/       # 上传模式测试
└── test_music/              # 音乐测试
```

## 特性

| 模块 | 说明 |
|:---|:---|
| `fwfii.quick` | 一键连接/断开/编译/上传 |
| `fwfii.fc` | 飞行控制 (起飞/降落/移动/空翻/特技) |
| `fwfii.led` | LED 灯光 (常亮/闪烁/呼吸/跑马灯/机身灯/电机灯) |
| `fwfii.swarm` | 蜂群项目 — 批量编译/上传/同步起飞+音乐 |
| `fwfii.offline_multi` | ★ 离线多机 — 一个 .py 编写全部无人机，自动拆分为独立脚本 |
| `fwfii.gtrfs_compat` | gtrfs 兼容层 — 直接运行 gtrfs/官方脚本 |
| `fwfii.fii_exporter` | ★ .fii 项目导出 — 生成官方炫舞软件项目文件 + Blockly XML |
| `fwfii.planning` | 离线任务编译 (.py → .ls) + WiFi/串口上传 |
| `fwfii.utils.logger` | 遥测数据记录 (CSV: 时间/位置/电量/状态) |
| `fwfii.utils.music` | 背景音乐播放 (mp3/flac/wav，蜂群表演) |
| `fwfii.fc.position_viewer` | OpenCV 三视图 (俯视/前视/右视 + 轨迹) |
| `fwfii.fc.monitor` | 多机仪表盘 (Curses/Matplotlib) |

## 安装

```bash
pip install -e .
```

依赖: Python ≥ 3.6, pyserial ≥ 3.5, numpy, opencv-python, pygame (音乐)

## 快速开始

### 在线飞行 (实时控制)

```python
from fwfii import connect, disconnect, Flight
from fwfii import Arm, Takeoff, Land, ProgrammingMode, Delay
from fwfii import AllOn, AllOff, GREEN

# 连接 (uavid = group*1000+number, IP = 192.168.group.number)
d, h, f1 = connect(71101)
f1.position = (20, 20, 0, 0)

# 飞行
ProgrammingMode(f1); Delay(500)
Arm(f1); Delay(2000)
AllOn(f1, GREEN)            # 绿灯
Takeoff(f1, 80)             # 起飞 80cm
Delay(4000)
Land(f1); Delay(5000)
AllOff(f1)
Disarm(f1)

disconnect()
```

顶层包 `fwfii` 已导出所有常用 API，一行导入即可：

```python
from fwfii import (
    connect, disconnect, plan, deliver,    # 快捷操作
    Flight,                                 # 无人机
    Arm, Disarm, Takeoff, Land, Move2,     # 飞行指令
    Delay,                                  # 延时
    AllOn, AllOff, RED, GREEN, BLUE,       # LED + 颜色
    start_log, stop_log,                    # 遥测
    MultiPlan, SwarmProject,               # 多机
)
```

## 飞行指令

### 基本动作

| 函数 | 说明 |
|:---|:---|
| `Arm(f)` | 解锁电机 |
| `Disarm(f)` | 上锁电机 |
| `Takeoff(f, alt)` | 起飞到指定高度 (cm) |
| `Land(f)` | 降落 |
| `Stop(f)` | 紧急停机 |
| `Hover(f)` | 悬停 |

### 移动

| 函数 | 说明 |
|:---|:---|
| `Move2(f, x, y, z)` | 飞到绝对坐标 (cm) |
| `MoveDelta(f, dx, dy, dz)` | 相对位移 (cm) |
| `Forward(f, d)` / `Backward(f, d)` | 前/后 d cm |
| `Left(f, d)` / `Right(f, d)` | 左/右 d cm |
| `Up(f, d)` / `Down(f, d)` | 上/下 d cm |

### 旋转 & 特技

| 函数 | 说明 |
|:---|:---|
| `Yaw(f, 'l'/'r', angle)` | 旋转 (角度) |
| `Yaw2(f, 'l'/'r', angle)` | 旋转到绝对角度 |
| `Flip(f, 'x'/'-x')` | 前空翻 / 后空翻 |
| `Nod(f, axis, d)` | 点头动作 |
| `SimpleHarmonic(f, axis, amp, omega, ...)` | 简谐运动 |
| `CylindricalSpiral(f, axis, marker, ...)` | 圆柱螺旋 |
| `RoundInAir(f, x, y, cx, cy, h, dir, speed)` | 空中盘旋 |
| `MovewHeading(f, axis, d, clockwise, angle)` | 带旋转移动 |

### 速度/加速度

| 函数 | 范围 |
|:---|:---|
| `MaxVelXY(f, v)` | 水平速度 0~500 cm/s |
| `MaxVelZ(f, v)` | 垂直速度 0~300 cm/s |
| `MaxAccXY(f, a)` | 水平加速度 0~500 cm/s² |
| `MaxAccZ(f, a)` | 垂直加速度 0~500 cm/s² |
| `MaxAngularRate(f, w)` | 角速度 0~120 deg/s |

### 飞行模式

| 函数 | 模式 | 用途 |
|:---|:---|:---|
| `ProgrammingMode(f)` | GUIDED (4) | 在线编程控制 |
| `PlanningMode(f)` | AUTO (3) | 离线任务执行 |

### 任务控制

| 函数 | 说明 |
|:---|:---|
| `MissionStart(f)` | 启动上传的离线任务 |
| `MissionContinue(f)` | 继续暂停的任务 |
| `MissionPause(f)` | 暂停任务 |
| `DelayLaunch(seg, delta)` | 延时启动 (多机同步) |

## LED 灯光

```python
from fwfii import (
    AllOn, AllOff, AllBlink, AllBreath,
    BodyOn, BodyOff, BodyBlink, BodyBreath,
    MotorOn, MotorOff, MotorBlink, MotorBreath, MotorHorse,
    RED, GREEN, BLUE, YELLOW, CYAN, PURPLE, WHITE, ORANGE, PINK,
)
```

| 函数 | 说明 |
|:---|:---|
| `AllOn(f, color)` / `AllOff(f)` | 全灯常亮/灭 |
| `AllBlink(f, color, on_ms, off_ms)` | 全灯闪烁 |
| `AllBreath(f, color, on_ms, off_ms)` | 全灯呼吸 |
| `BodyOn(f, color)` / `BodyOff(f)` | 机身灯常亮/灭 |
| `BodyBlink(f, color, on_ms, off_ms)` | 机身灯闪烁 |
| `BodyBreath(f, color, on_ms, off_ms)` | 机身灯呼吸 |
| `MotorOn(f, id, color)` / `MotorOff(f, id)` | 电机灯 (id: 0=四灯, 1-4=单灯) |
| `MotorBlink(f, id, color, on_ms, off_ms)` | 电机灯闪烁 |
| `MotorBreath(f, id, color, on_ms, off_ms)` | 电机灯呼吸 |
| `MotorHorse(f, [colors], clockwise, duration)` | 跑马灯 |

颜色常量: `RED=0xFF0000`, `GREEN=0x00FF00`, `BLUE=0x0000FF`, `YELLOW=0xFFFF00`,
`CYAN=0x00FFFF`, `PURPLE=0xFF00FF`, `WHITE=0xFFFFFF`, `ORANGE=0xFF8000`, `PINK=0xFF0080`

## 离线任务 (plan + deliver)

### 编译

```python
from fwfii import plan

plan("my_mission.py", "./output")
# → output/71101.ls
```

任务脚本支持 **ts + Delay 混用**，`plan()` 自动为没有 ts 的指令分配时间戳：

```python
from fwfii import Flight, Arm, Disarm, Takeoff, Land, Move2, Delay
from fwfii import AllOn, AllOff, GREEN, RED

f1 = Flight(71101)

# 精确卡点 — 灯光在第 0ms 亮
AllOn(f1, GREEN, ts=0)
Arm(f1, ts=500)

# 自然等待 — 后续指令自动累加时间戳
Delay(2000)                        # ts ≈ 2500
Takeoff(f1, 80)

Delay(5000)                        # ts ≈ 7500
Move2(f1, 30, 10, 80)

Delay(3000)                        # ts ≈ 10500
Move2(f1, 10, 30, 80)

# 混用 — 灯光精确卡第 15 秒, 移动自动跟随
AllOn(f1, RED, ts=15000)
Move2(f1, 20, 20, 60)

Delay(3000)
Land(f1)                           # ts ≈ 18000

Delay(5000)
Disarm(f1)                         # ts ≈ 23000
```

### 上传

```python
from fwfii import deliver

deliver(71101, "./output")
# → Transfer 头 + 文件数据 → TCP port 10034
```

### 执行

```python
from fwfii import connect, disconnect, PlanningMode, MissionStart, Delay

d, h, f1 = connect(71101)
PlanningMode(f1); Delay(500)
MissionStart(f1)     # 无人机自动执行脚本
# ... 监控位置 ...
disconnect()
```

## 离线多机任务 (MultiPlan) ★

**一个 `.py` 文件编写全部无人机的飞行脚本** (ts + Delay 可混用)，自动拆分为各无人机独立的 `.py` + `.ls` + 完整项目结构。

```python
from fwfii.offline_multi import MultiPlan

# 配置项目
mp = MultiPlan()
mp.add_drone(71101, pos=(20, 20))
mp.add_drone(71102, pos=(40, 20))
mp.set_music("bgm.mp3")
mp.set_carpet(80)

# 一键构建
mp.build("choreography.py", "./my_show")
```

### 统一脚本格式

和单机离线脚本完全一样的写法，只是创建多个 `Flight` 对象：

```python
# choreography.py — 一个文件编写全部无人机
from fwfii import Flight, Arm, Takeoff, Land, Move2, Delay
from fwfii import AllOn, AllOff, RED, GREEN, BLUE

f1 = Flight(71101)
f2 = Flight(71102)

MaxVelXY(f1, 50); MaxVelXY(f2, 80)
Arm(f1); Arm(f2)
Delay(2000)
Takeoff(f1, 80); Takeoff(f2, 120)
Delay(5000)
Move2(f1, 30, 10, 80)
Move2(f2, 10, 30, 120)
# ... 编队动作 ...
Land(f1); Land(f2)
```

### 编译输出

```
my_show/
├── project.json              # 项目元数据
├── scripts/                  # 自动生成的 per-drone .py
│   ├── drone_71101.py
│   └── drone_71102.py
├── 71101.ls                  # 编译好的二进制
└── 71102.ls                  # 编译好的二进制
```

## 蜂群飞行 (SwarmProject)

从 pyfii `.fii` 项目加载，或手动编程，批量管理多架无人机：

```python
from fwfii import SwarmProject

# 方式 1: 从 pyfii 项目加载
swarm = SwarmProject("E:/F流浪地球")
swarm.info()

# 方式 2: 手动创建
swarm = SwarmProject()
swarm.add_drone(71101, "drone1.py", pos=(20, 20))
swarm.add_drone(71102, "drone2.py", pos=(40, 20))
swarm.set_music("music.mp3")

# 方式 3: 结合 MultiPlan 使用
from fwfii import MultiPlan
mp = MultiPlan()
mp.add_drone(71101, pos=(20, 20))
mp.add_drone(71102, pos=(40, 20))
mp.build("unified.py", "./output")

swarm = SwarmProject()
for d in mp._drones:
    swarm.add_drone(d, f"./output/scripts/drone_{d}.py",
                    pos=mp._drones[d]['pos'])
swarm.set_music("music.mp3")

# 批量操作
swarm.compile("./output")           # 编译全部 .py → .ls
swarm.deliver()                      # 上传全部 .ls 到各自 IP
swarm.launch_with_music(countdown=5) # 连接 + PlanningMode + 倒计时 + 同步起飞 + 音乐

# 断开
swarm.disconnect_all()
```

## 遥测记录

```python
from fwfii import start_log, stop_log

start_log(save_dir="./flight_logs", script_path=__file__)
# ... 飞行 ...
stop_log()
# → flight_logs/flight_20260101_120000/
#     ├── script.py       (飞行脚本副本)
#     └── telemetry.csv   (时间 / 位置 / 电量 / 状态 / 模式)
```

## 实时位置预览

```python
from fwfii import PositionViewer, set_beat_output

set_beat_output("slow")    # 心跳降频
viewer = PositionViewer(programmable=360, scale=1.0)
viewer.start()
# ... 飞行，三视图窗口实时显示 ...
viewer.stop()
```

## 音乐播放 (蜂群表演)

```python
from fwfii import load_music, play_music, stop_music, set_music_volume

load_music("music.flac")
set_music_volume(0.7)
play_music(loops=0)       # 0=单次, -1=循环
# ...
stop_music(fade_ms=2000)
```

## Fii 项目导出 (FiiExporter) ★

将 fwfii 飞行脚本导出为官方 **小鸟飞飞图形化编程炫舞软件** 的 `.fii` 完整项目文件。
**不依赖任何第三方库**，生成包含 Blockly 可视化块的完整项目。

### 从 per-drone 脚本导出

```python
from fwfii import FiiExporter, fwfii_to_fii

# 方式 1: 便捷函数
fwfii_to_fii(
    scripts=["drone1.py", "drone2.py"],
    uavids=[98101, 98102],
    positions=[(100, 100), (460, 100)],
    output_dir="./my_show",
    music="music.mp3",
    carpet=560,              # 40/80/360/560
)

# 方式 2: FiiExporter 类
fii = FiiExporter("my_show")
fii.add_drone(98101, "drone1.py", pos=(100, 100))
fii.add_drone(98102, "drone2.py", pos=(460, 100))
fii.set_music("music.mp3")
fii.set_carpet(560)
fii.build("./output")
```

### 完整工作流: 统一脚本 → .fii

```python
from fwfii import MultiPlan, FiiExporter

# Step 1: 统一脚本 → per-drone .py + .ls
mp = MultiPlan()
mp.add_drone(98101, pos=(100, 100))
mp.add_drone(98102, pos=(460, 100))
mp.set_carpet(560)
mp.build("choreography.py", "./output")

# Step 2: per-drone .py → .fii 项目
fii = FiiExporter("my_show")
for uavid in [98101, 98102]:
    fii.add_drone(uavid, f"./output/scripts/drone_{uavid}.py")

fii.set_music("music.mp3")
fii.set_carpet(560)
fii.build("./fii_output")

# → 用官方炫舞软件打开 ./fii_output/my_show.fii
```

### 实时模式脚本也支持

```python
# 同一个 .py 文件，延时写法或 ts= 写法都可以
f1 = Flight(98101)

Arm(f1)                         # 无 ts → 自动从 Delay 推断
Delay(3000)
Takeoff(f1, 120)
Delay(5000)
Move2(f1, 280, 280, 130)
# ... → FiiExporter 直接导出 .fii
```

### 输出结构

```
output/
├── my_show.fii                  # 项目清单 XML
└── 动作组/
    ├── checksums.xml
    ├── music.mp3
    ├── 动作组1/
    │   ├── webCodeAll.py       # gtrfs 飞行脚本
    │   └── webCodeAll.xml      # 完整 Blockly 可视化块
    └── 动作组2/ ...
```

### 读取已有 .fii 项目

```python
from fwfii import FiiExporter, SwarmProject

# 方式 1: FiiExporter.load() → dict
info = FiiExporter.load("./my_show")
for d in info['drones']:
    print(d['uavid'], d['pos'])

# 方式 2: SwarmProject.load() → 可编译/上传/执行
swarm = SwarmProject()
swarm.load("./my_show")
swarm.compile("./output")
swarm.deliver()
```

### 定位毯映射

| `set_carpet(n)` | .fii AreaL/AreaW | AreaH |
|---|---|---|
| 40 | 73 | 300 |
| 80 | 115 | 300 |
| 360 | 400 | 300 |
| 560 | 600 | 300 |

### gtrfs 兼容

```python
from fwfii.gtrfs_compat import *

# 直接运行 gtrfs/官方软件生成的脚本
f1 = Flight(1001)
Arm(f1); Delay(1000)
Takeoff(f1, 80)
# ... 所有 gtrfs API 都可直接使用
```

## 多机在线编队

```python
from fwfii import connect, disconnect

f1 = Flight(71101)  # 192.168.71.101
f2 = Flight(71102)  # 192.168.71.102

d1, h1, f1 = connect(71101)
d2, h2, f2 = connect(71102)
# 共享 TcpDelivery + HeartBeat，自动路由到对应的 IP

# 编队飞行 (在线模式)
for f in (f1, f2):
    ProgrammingMode(f); Delay(300)
Arm(f1); Arm(f2); Delay(2000)
Takeoff(f1, 80); Takeoff(f2, 120)  # 分层: Z 差 >= 50cm
Delay(4000)
# ... 编队动作 ...
Land(f1); Land(f2)
disconnect()
```

## 示例脚本

| 目录 | 文件 | 说明 |
|:---|:---|:---|
| — | `beginner_guide.py` | ★ 新手大全 (10 节交互式教程) |
| `01_basics/` | `hello_drone.py` | 连接→起飞→悬停→降落 |
| | `led_test.py` | LED 通信测试 |
| | `monitor_position.py` | 实时位置监控 (无飞行) |
| | `emergency_stop.py` | 紧急停机 |
| | `emergency_land.py` | 紧急降落 |
| `02_carpet_flight/` | `simple_square.py` | 定位毯正方形航线 |
| | `multi_point_flight.py` | 25 点多速采集 |
| | `trajectory_collect.py` | 网格/螺旋/Z阶梯航线 → CSV |
| | `fly_no_carpet.py` | 无定位毯相对飞行 |
| `03_mission/` | `compile_and_upload.py` | 完整流程: plan → deliver → execute |
| `04_swarm/` | `dance_duet.py` | 双机编队舞蹈 (灯光+音乐+空翻+安全分层) |
| `05_utils/` | `connect_and_fly.py` | 最简飞行 (起飞→悬停 3s) |
| | `test_battery.py` | 电池电压测试 |
| | `position_viewer_demo.py` | OpenCV 三视图预览 |
| `06_offline_multi/` | `dual_square.py` | ★ 统一多机脚本: 双机正方形编队 |
| | `demo_build.py` | MultiPlan 构建演示 |
| `missions/` | `square_mission.py` | ts+Delay 混用离线任务脚本 |

## 无人机 ID 规则

```
IP: 192.168.{group}.{number}
ID = group × 1000 + number

例: 192.168.71.101 → 71101
    192.168.95.1   → 95001
    192.168.1.200  → 1200
```

## 定位毯 (Carpet)

| 尺寸 | 坐标范围 | 适用机型 |
|:---|:---|:---|
| 40 cm | (0,0) ~ (40,40) | F400 |
| 80 cm | (0,0) ~ (80,80) | F400 |
| 360 cm | (0,0) ~ (360,360) | F600 |
| 560 cm | (0,0) ~ (560,560) | F600 |

## 安全

- 🔋 飞行前确认电池充足 (> 30%)
- 📍 室内必须使用定位毯
- 🐢 首次飞行低空慢速 (< 100cm, 速度 < 50 cm/s)
- 🛑 随时 `Ctrl+C` 中断或运行 `emergency_stop.py`
- 👀 保持视距内观察
- 📏 多机编队: Z 差 >= 50cm 或 XY 距 >= 40cm

## 故障排查

| 问题 | 可能原因 | 解决 |
|:---|:---|:---|
| 连接失败 | 未连无人机 WiFi | 检查 WiFi 192.168.x.x |
| 连接超时 | 无人机未开机 | 检查电源 |
| 位置全是 0 | 未放定位毯 / 未取得定位 | 放到定位毯上，等待定位灯常亮 |
| 上传后桨转就停 | .ls 时间戳全为 0 | 任务脚本使用 ts 参数或 Delay |
| LED 不亮 | Emergency 通道未通 | 先跑一次 connect |
| 音乐无声 | pygame 未安装 | `pip install pygame` |

## 版本历史

### v1.3.1 (2026-07-13)

- **修复** `_parse_fwfii_color` 不再自动把普通整数转成 hex 颜色（如 `250 → #0000fa`），避免速度/时长被误转
- **修复** `_parse_fwfii_script` 混合模式：Delay + 显式 `ts=` 混用时，非 ts 命令从 Delay 时钟正确推算，不再全部归零
- **修复** `_to_webcodeall_xml` 中未知命令导致 `prev_ts` 不更新的 bug
- **改进** 移除 pyfii 适配功能，FiiExporter 原生支持 .fii 导出 + Blockly XML

### v1.3.0

- **新增** `FiiExporter` — 原生 .fii 官方项目导出，含 Blockly XML 可视化块
- **新增** 混合模式支持：`plan()` 同时支持 ts + Delay
- **新增** `offline_multi.py` — MultiPlan 离线多机统一脚本自动拆分

## License

MIT
