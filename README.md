# fwfii — Fii Drone Flight Control SDK

Python 飞行控制库，适用于小鸟飞飞 (Fii) F400/F600 教育无人机。**完全脱离原版图形化软件**，纯 Python 控制。

## 特性

| 模块 | 说明 |
|:---|:---|
| `fwfii.quick` | 一键连接/断开/编译/上传 |
| `fwfii.fc` | 飞行控制 (起飞/降落/移动/特技) |
| `fwfii.led` | LED 灯光 (常亮/闪烁/呼吸/跑马灯) |
| `fwfii.utils.logger` | 遥测数据记录 (CSV) |
| `fwfii.utils.music` | 背景音乐播放 (蜂群表演) |
| `fwfii.planning` | 离线任务编译 + 上传 |

## 安装

```bash
pip install -e .
```

依赖: Python ≥ 3.6, pyserial ≥ 3.5

## 快速开始

```python
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.led.lamp import AllOn, AllOff
from fwfii.utils import Delay

# 连接 (uavid = group*1000+number, IP = 192.168.group.number)
d, h, f1 = connect(71101)
f1.position = (20, 20, 0, 0)

# 飞行
ProgrammingMode(f1)
Arm(f1); Delay(2000)
AllOn(f1, 0x00FF00)       # 绿灯
Takeoff(f1, 80)            # 起飞 80cm
Delay(4000)
Land(f1); Delay(5000)
AllOff(f1)
Disarm(f1)

disconnect()
```

## connect / disconnect

```python
from fwfii.quick import connect, disconnect

# 单机
d, h, f1 = connect(98101)

# 多机 (共享一条 TcpDelivery + HeartBeat)
d1, h1, f1 = connect(98101)
d2, h2, f2 = connect(98102)

# 断开全部
disconnect()
```

## 飞行指令

| 函数 | 说明 |
|:---|:---|
| `Arm(f)` | 解锁电机 |
| `Disarm(f)` | 上锁电机 |
| `Takeoff(f, alt)` | 起飞到指定高度 (cm) |
| `Land(f)` | 降落 |
| `Move2(f, x, y, z)` | 飞到绝对坐标 |
| `Forward(f, d)` / `Backward(f, d)` | 前/后 d cm |
| `Left(f, d)` / `Right(f, d)` | 左/右 d cm |
| `Up(f, d)` / `Down(f, d)` | 上/下 d cm |
| `Hover(f)` | 悬停 |
| `Yaw(f, dir, angle)` | 旋转 (dir='l'/'r', angle=角度) |
| `Flip(f, axis)` | 空翻 (axis='x'/'-x') |

### 速度/加速度

| 函数 | 范围 |
|:---|:---|
| `MaxVelXY(f, v)` | 水平速度 0~500 cm/s |
| `MaxVelZ(f, v)` | 垂直速度 0~300 cm/s |
| `MaxAccXY(f, a)` | 水平加速度 0~500 cm/s² |
| `MaxAccZ(f, a)` | 垂直加速度 0~500 cm/s² |

### 飞行模式

| 函数 | 模式 | 用途 |
|:---|:---|:---|
| `ProgrammingMode(f)` | GUIDED (4) | 在线编程控制 |
| `PlanningMode(f)` | AUTO (3) | 离线任务执行 |

### 特技

| 函数 | 说明 |
|:---|:---|
| `Flip(f, 'x')` | 前空翻 |
| `Flip(f, '-x')` | 后空翻 |
| `SimpleHarmonic(f, axis, ...)` | 简谐运动 |
| `CylindricalSpiral(f, axis, ...)` | 圆柱螺旋 |

### 任务控制

| 函数 | 说明 |
|:---|:---|
| `MissionStart(f)` | 启动上传的任务 |
| `MissionContinue(f)` | 继续暂停的任务 |
| `MissionPause(f)` | 暂停任务 |
| `DelayLaunch(seg, delta)` | 延时启动 (多机同步) |

## LED 灯光

```python
from fwfii.led.lamp import (
    AllOn, AllOff, AllBlink, AllBreath,
    BodyOn, BodyOff, BodyBlink, BodyBreath,
    MotorOn, MotorOff, MotorBlink, MotorBreath, MotorHorse
)

# 颜色: 0xRRGGBB
RED = 0xFF0000; GREEN = 0x00FF00; BLUE = 0x0000FF
YELLOW = 0xFFFF00; WHITE = 0xFFFFFF

AllOn(f1, RED)                     # 全灯常亮
AllBlink(f1, BLUE, 300, 300)       # 全灯闪烁 (on/off ms)
AllBreath(f1, GREEN, 800, 800)     # 全灯呼吸
BodyOn(f1, YELLOW)                 # 机身灯
MotorOn(f1, 0, WHITE)              # 四电机全白
MotorHorse(f1, [RED,GREEN,BLUE,YELLOW], True, 600)  # 跑马灯
AllOff(f1)                         # 灭灯
```

## 离线任务: plan + deliver

### 编译

```python
from fwfii.quick import plan

plan("my_mission.py", "./output")
# → output/71101.ls
```

任务脚本 (`my_mission.py`) 使用绝对时间戳 `ts`:

```python
from fwfii.fc import Flight, Takeoff, Land, Move2, Arm, Disarm
from fwfii.led.lamp import AllOn, AllOff

f1 = Flight(71101)

Arm(f1, ts=500)                    # ts=500ms
Takeoff(f1, 80, ts=2500)           # ts=2500ms
Move2(f1, 30, 10, 80, ts=7500)    # ts=7500ms
Move2(f1, 10, 30, 80, ts=10500)
Land(f1, ts=14500)
Disarm(f1, ts=19500)
AllOff(f1, ts=19500)
```

### 上传

```python
from fwfii.quick import deliver

deliver(71101, "./output")
# → Transfer 头 + 文件数据 → port 10034
```

### 执行

```python
from fwfii.quick import connect, disconnect
from fwfii.fc import PlanningMode, MissionStart
from fwfii.utils import Delay

d, h, f1 = connect(71101)
PlanningMode(f1); Delay(500)
MissionStart(f1)     # 无人机自动执行脚本
# ... 任务完成后自动上锁 ...
disconnect()
```

## 遥测记录

```python
from fwfii.quick import start_log, stop_log

start_log(save_dir="./flight_logs", script_path=__file__)
# ... 飞行 ...
stop_log()
# → flight_logs/flight_20260101_120000/
#     ├── script.py       (飞行脚本副本)
#     └── telemetry.csv   (时间/位置/电量/状态)
```

## 音乐播放 (蜂群表演)

```python
from fwfii.quick import load_music, play_music, stop_music, set_music_volume

load_music("music.flac")
set_music_volume(0.7)
play_music(loops=0)       # 0=单次, -1=循环
# ...
stop_music(fade_ms=2000)
```

## 示例脚本

| 文件 | 说明 |
|:---|:---|
| `examples/test_40x40_flight.py` | 40×40 定位毯起降测试 |
| `examples/test_40x40_deliver.py` | plan→deliver→execute 完整流程 |
| `examples/swarm_dance.py` | 双机编队舞蹈 (灯光+音乐+空翻) |
| `examples/multi_point_flight.py` | 25 点多速采集 |
| `examples/trajectory_collect.py` | 网格/螺旋/阶梯航线 |
| `examples/connect_and_fly.py` | 最简飞行 |
| `examples/fly_with_carpet.py` | 定位毯正方形航线 |
| `examples/led_test.py` | LED 通信测试 |
| `examples/monitor_position.py` | 实时位置监控 |
| `examples/emergency_stop.py` | 紧急停机 |

## 无人机 ID 规则

```
IP: 192.168.group.number
ID = group × 1000 + number

例: 192.168.71.101 → 71101
    192.168.1.200  → 1200
```

## 安全

- 🔋 飞行前确认电池充足
- 📍 室内必须使用定位毯
- 🐢 首次飞行低空慢速 (< 100cm)
- 🛑 随时 `Ctrl+C` 中断或运行 `emergency_stop.py`
- 👀 保持视距内观察

## 故障排查

| 问题 | 可能原因 | 解决 |
|:---|:---|:---|
| 连接失败 | 未连无人机 WiFi | 检查 WiFi 192.168.x.x |
| 连接超时 | 无人机未开机 | 检查电源 |
| 位置全是 0 | 未放定位毯 | 放到定位毯上 |
| 上传后桨转就停 | 时间戳全为 0 | 任务脚本用 ts 参数 |
| LED 不亮 | Emergency 通道未通 | 先跑一次 connect |

## 多机编队

```python
f1 = Flight(71101)  # 192.168.71.101
f2 = Flight(71102)  # 192.168.71.102

d1, h1, f1 = connect(71101)
d2, h2, f2 = connect(71102)
# 共享 TcpDelivery + HeartBeat，自动路由
```

## License

MIT
