# fwfii - Fii Drone Flight Control SDK

Python 飞行控制库，适用于小鸟飞飞 (Fii) F400/F600 教育无人机。

**完全脱离原版图形化软件**，通过 Python 脚本直接控制无人机飞行。

## ✨ 特性

- 🚁 **在线实时控制** - TCP/WiFi 直连，逐条发送指令
- 📍 **定位毯精准定位** - 室内厘米级坐标
- 📦 **离线任务上传** - 编译→上传→自主执行，适合多机编队
- 🎯 **绝对坐标飞行** - Move2 精确飞到目标点
- 🔄 **相对移动** - 无定位毯也能飞
- 💡 **LED 灯光控制** - AllOn/AllOff/Blink/Breath
- 🌀 **空翻** - 支持左右侧翻
- 📡 **实时状态监控** - 位置、电量、飞行模式
- 🆘 **紧急停机** - 一键停止所有电机

## 📦 安装

```bash
pip install fwfii
```

或从源码安装：

```bash
git clone <repo-url>
cd fwfii_package
pip install -e .
```

依赖：Python >= 3.6，pyserial >= 3.5（串口模式需要）

## 🚀 快速开始
### 硬件准备

|项目| 说明               |
|:---:|:-----------------|
|无人机| F400 或 F600，电池充足 |
|定位毯| 室内飞行必备           |
|网络| 电脑连接无人机所在 WiFi/路由器|

### 无人机 ID 规则

```text
IP 地址: 192.168.group.number
ID = group × 1000 + number

示例:
  192.168.71.101 → ID = 71101
  192.168.1.200  → ID = 1200
  ```

### 30 秒起飞

```python
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.utils import *

d, h, f1 = connect(71101)
f1.position = (0, 0, 0, 0)

SetFlightMode(f1, 4)
Delay(500)
Arm(f1)
Delay(2000)
Takeoff(f1, 100)
Delay(5000)
Land(f1)
Delay(5000)
Disarm(f1)

disconnect()
```

## 📚 API 文档

### 快捷连接

```python
from fwfii.quick import connect, disconnect

d, h, f1 = connect(71101)   # 连接 + 启动心跳
# ... 飞行 ...
disconnect()                 # 断开所有连接
disconnect(71101)            # 断开指定无人机
```

### 通用飞行 API
* ts 和 emergency 参数说明：
* ts：时间戳，在线模式固定为 0，离线模式填写绝对时间戳（毫秒） 
* emergency：在线模式用 True（实时），离线模式用 False 
* ⚠️ Delay 和时间戳不可混用

API|功能|示例
---|---|---
Flight(uavid)|创建飞行器对象|f1 = Flight(71101)
Delay(ms)|延时毫秒|Delay(1000)
ProgrammingMode(flight)|切换在线编程模式|ProgrammingMode(f1)
Arm(flight)|解锁|Arm(f1)
Disarm(flight)|上锁|Disarm(f1)
Takeoff(flight, alt)|起飞(cm)|Takeoff(f1, 120)
Land(flight)|降落|Land(f1)
Stop(flight, emergency=True)|紧急停桨|Stop(f1, emergency=True)
Move2(flight, x, y, z)|飞到绝对坐标(cm)|Move2(f1, 50, 50, 100)
MoveDelta(flight, dx, dy, dz)|相对移动(cm)|MoveDelta(f1, 30, 0, 0)
Forward(flight, d)|前进 d cm|Forward(f1, 50)
Backward(flight, d)|后退 d cm|Backward(f1, 30)
Left(flight, d)|左移 d cm|Left(f1, 30)
Right(flight, d)|右移 d cm|Right(f1, 30)
Up(flight, d)|上升 d cm|Up(f1, 20)
Down(flight, d)|下降 d cm|Down(f1, 20)
Hover(flight)|悬停|Hover(f1)
AddMark(name, x, y, z)|添加标记点|AddMark("A", 50, 50, 100)
Move2Marker(flight, name)|飞到标记点|Move2Marker(f1, "A")
MaxVelXY(flight, v)|水平速度(cm/s, 0~500)|MaxVelXY(f1, 200)
MaxAccXY(flight, a)|水平加速度(cm/s², 0~500)|MaxAccXY(f1, 200)
MaxVelZ(flight, v)|垂直速度(cm/s, 0~300)|MaxVelZ(f1, 100)
MaxAccZ(flight, a)|垂直加速度(cm/s², 0~500)|MaxAccZ(f1, 200)
MaxAngularRate(flight, w)|角速度(°/s, 0~120)|MaxAngularRate(f1, 90)
Yaw(flight, dir, angle)|相对转向(°), dir='l'/'r'|Yaw(f1, 'l', 90)
Yaw2(flight, dir, angle)|绝对转向(°)|Yaw2(f1, 'r', 180)
Flip(flight, axis)|空翻 'x'/'-x'|Flip(f1, 'x')
Rotation_Delta(flight, x, y, z)|姿态旋转(°)|Rotation_Delta(f1, 360, 0, 0)
DelayLaunch(seg, delta)|离线同步指令|DelayLaunch(71, 5000)

### F600 灯光 API

```python
from fwfii.led.lamp import *
```

API|功能|示例
---|---|---
AllOn(f, color)|全亮|AllOn(f1, 0xFF0000)
AllOff(f)|全灭|AllOff(f1)
AllBlink(f, color, A, B)|全闪烁，A/B=亮/灭ms|AllBlink(f1, 0xFF0000, 500, 500)
AllBreath(f, color, A, B)|全呼吸，A/B=暗→亮/亮→暗ms|AllBreath(f1, 0x00FF00, 1000, 1000)
BodyOn(f, color)|机身亮|BodyOn(f1, 0x0000FF)
BodyOff(f)|机身灭|BodyOff(f1)
BodyBlink(f, color, A, B)|机身闪烁|BodyBlink(f1, 0xFFFF00, 300, 700)
BodyBreath(f, color, A, B)|机身呼吸|BodyBreath(f1, 0xFF00FF, 800, 800)
MotorOn(f, id, color)|电机亮(id:1-4,0=全)|MotorOn(f1, 1, 0xFF0000)
MotorOff(f, id)|电机关|MotorOff(f1, 1)

### F400 灯光 API

```python
from fwfii.led.led import *
```

API|功能|示例
---|---|---
TurnOnSingle(f, led, color)|亮单灯(1-12)|TurnOnSingle(f1, 1, 0xFF0000)
TurnOffSingle(f, led)|关单灯|TurnOffSingle(f1, 1)
TurnOnAll(f, colors)|全亮(12色列表)|TurnOnAll(f1, [0xFF0000]*12)
TurnOffAll(f)|全灭|TurnOffAll(f1)
BlinkSingle(f, led, color)|单灯闪烁|BlinkSingle(f1, 3, 0x00FF00)
BlinkFastAll(f, colors)|全快闪|BlinkFastAll(f1, colors)
BlinkSlowAll(f, colors)|全慢闪|BlinkSlowAll(f1, colors)
Breath(f, leds, colors)|指定灯呼吸|Breath(f1, [1,2], [0xFF0000, 0x0000FF])
HorseRace(f, colors)|跑马灯|HorseRace(f1, colors)

### 无人机属性

```python
f1.position       # (x, y, z, yaw) 厘米 + 百分之一度
f1.position = (...) # 手动设置初始位置
f1.flightmode     # 飞行模式字符串
f1.fcstatus       # 飞控状态
f1.gpsstatus      # 定位状态
f1.voltage        # 电池电压 (mV)
```

## 📂 示例脚本

文件|说明
---|---
connect_and_fly.py|最简起飞
fly_with_carpet.py|定位毯航线
fly_no_carpet.py|无定位毯飞行
flip.py|空翻测试
led_test.py|LED 测试
monitor_position.py|位置监控
emergency_stop.py|紧急停机
emergency_land.py|紧急降落
mission/mission_upload.py|离线任务上传
mission/mission.py|离线任务模板

## ⚠️ 注意事项

### 安全
* 🔋 确认电池充足
* 📍 室内飞行必须使用定位毯 
* 🐢 首次飞行低空慢速（< 100cm） 
* 🛑 随时准备运行 emergency_stop.py

### 空翻

* 仅支持 x/-x 轴（左右侧翻） 
* 高度至少 150cm

## 📄 License

MIT

```text
MIT License

Copyright (c) 2024 fwfii

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```