# fwfii - Fii Drone Flight Control SDK

Python 飞行控制库，适用于小鸟飞飞 (Fii) F400/F600 教育无人机。

**完全脱离原版图形化软件**，通过 Python 脚本直接控制无人机飞行。

## ✨ 特性

- 🚁 **TCP/WiFi 实时控制** - 支持单机和多机编队
- 📍 **定位毯精准定位** - 室内厘米级定位
- 🎯 **绝对坐标飞行** - Move2 精确飞到目标点
- 🔄 **相对移动** - 无定位毯也能飞
- 📡 **实时状态监控** - 位置、电量、飞行模式
- 🆘 **紧急停机** - 一键停止所有电机

## 📦 安装

### 从源码安装

```bash
git clone <your-repo-url>
cd fwfii_package
pip install -e .
```
依赖
Python >= 3.6

pyserial >= 3.5（串口模式需要）

## 🚀 快速开始
1. 硬件准备

|  项目   | 说明                 |
|:-----:|--------------------|
|  无人机  | F400 或 F600，电池充足   |
|  定位毯  | 室内飞行必备             |
|  网络   | 电脑连接无人机所在 WiFi/路由器 |
|  环境   | 光照充足，地面平坦          |

2. 无人机 ID 规则

```text
IP 地址: 192.168.group.number
ID = group × 1000 + number
```
示例:

  192.168.71.101 → ID = 71 × 1000 + 101 = 71101

  192.168.1.200  → ID = 1 × 1000 + 200  = 1200
3. 最简飞行（30 秒起飞）
```python
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight, Arm, Takeoff, Land, Disarm
from fwfii.fc.advanced import SetFlightMode
from fwfii.utils import Delay
import time
```
### 连接
```python
d = TcpDelivery(vo=None)
h = HeartBeat()
time.sleep(3)
```
### 创建无人机（修改为你的 ID）
```python
f1 = Flight(71101)
f1.position = (22, 22, 4, 0)  # 定位毯上的初始位置
```

### 切换模式 → 解锁 → 起飞 → 降落
```python
SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)
Takeoff(f1, 100)    # 起飞到 100cm
Delay(5000)
Land(f1)
Delay(5000)
Disarm(f1)

h.close()
d.close()
```
## 📚 API 文档
### 连接与初始化

| 类/函数                  | 说明                  |
|:----------------------|:--------------------|
| TcpDelivery(vo=None)  | TCP/WiFi 通信，多机编队必用  |
| HeartBeat()           | 心跳维持，持续收发状态         |
| Flight(id)            | 创建无人机对象             |

### 无人机属性
```python
f1 = Flight(71101)

f1.position       # (x, y, z, yaw) - 当前位置
f1.position = (x, y, z, yaw)  # 手动设置初始位置
f1.flightmode     # 当前飞行模式
f1.fcstatus       # 飞控状态
f1.gpsstatus      # GPS/定位状态
f1.voltage        # 电池电压 (mV)
f1.uavid          # 无人机 ID
```
### 飞行模式

|函数|模式|说明|
|:---|:---:|:---|
|SetFlightMode(f, 4)|GUIDED|编程控制模式（推荐）|
|ProgrammingMode(f)|GUIDED|同上，别名|
|PlanningMode(f)|AUTO|任务规划模式|

### 飞行指令

|函数|说明|示例|
|:---|:---|:---|
|Arm(f)|	解锁电机	|Arm(f1)|
|Disarm(f)|	上锁电机|	Disarm(f1)|
|Takeoff(f, alt)|	起飞到指定高度(cm)	|Takeoff(f1, 120)|
|Land(f)|	降落	|Land(f1)|
|Stop(f, emergency=True)|	紧急停机|	Stop(f1, emergency=True)|
|Move2(f, x, y, z)	|飞到绝对坐标|	Move2(f1, 50, 50, 100)|
|Forward(f, d)|	前进 d cm|	Forward(f1, 50)|
|Backward(f, d)	|后退 d cm	|Backward(f1, 30)|
|Left(f, d)	|左移 d cm	|Left(f1, 30)|
|Right(f, d)|	右移 d cm|	Right(f1, 30)|
|Up(f, d)|	上升 d cm	|Up(f1, 20)|
|Down(f, d)|	下降 d cm	|Down(f1, 20)|
|Hover(f)	|悬停	|Hover(f1)|

## 工具函数

|函数|说明|
|:---|:---|
|Delay(ms)|延时，单位毫秒
|AddMark(name, x, y, z)|添加标记点
|Move2Marker(f, name)|飞到标记点

### 📂 示例脚本
所有示例在 examples/ 目录下：

|文件|说明|
|:---|:---|
|connect_and_fly.py	|最简飞行示例|
|fly_with_carpet.py	|定位毯精确飞行（正方形航线）|
|fly_no_carpet.py	|无定位毯相对飞行|
|emergency_stop.py	|紧急停机|
|led_test.py	LED| 灯通信测试|
|monitor_position.py	|实时位置监控|

运行示例：

```bash
python examples/connect_and_fly.py
```

# ⚠️ 注意事项
## 安全

🔋 飞行前确认电池充足（> 11V）

📍 室内飞行必须使用定位毯

🐢 首次飞行建议低空慢速（< 100cm）

🛑 随时准备手动接管或运行 emergency_stop.py

👀 飞行时保持视距内观察

## 定位毯

确保光照充足，无强反光

定位毯表面保持清洁平整

无人机放在定位毯上会自动获取位置

无定位毯时只能用相对移动指令，精度取决于传感器

## 多机编队

所有无人机需在同一网段

每台无人机 IP 地址必须不同

创建多个 Flight 对象即可：

```python
f1 = Flight(71101)  # 192.168.71.101
f2 = Flight(71102)  # 192.168.71.102
f3 = Flight(71103)  # 192.168.71.103
```
## 🔧 故障排查

|问题|可能原因|解决|
|---|---|---|
|连接失败	|电脑未连无人机 WiFi|	检查网络连接|
|连接失败|无人机未开机|	检查无人机电源|
|位置全是 0	|未放定位毯上|	放回定位毯|
|位置全是 0	|光照不足|	改善光照|
|飞行动作不执行	|未切换 GUIDED 模式|	检查 SetFlightMode|
|飞行动作不执行	|未解锁	|检查 Arm()|
|LED 不亮	|Emergency 未初始化	|先用原版软件连接一次|

## 📄 License
MIT License - 详见 LICENSE

