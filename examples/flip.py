"""
空翻测试 - 飞到指定位置后右侧翻
注意：高度至少 150cm，定位毯必备！
"""
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.led.lamp import AllOn, AllOff
from fwfii.utils import *

DRONE_ID = 71101
INIT_POS = (0, 0, 0, 0)

RED=0xFF0000; GREEN=0x00FF00; BLUE=0x0000FF
YELLOW=0xFFFF00; CYAN=0x00FFFF; PURPLE=0xFF00FF

d, h, f1 = connect(DRONE_ID)
f1.position = INIT_POS

AllOn(f1, BLUE);     SetFlightMode(f1, 4); Delay(500)
AllOn(f1, YELLOW);   Arm(f1);              Delay(2000)
AllOn(f1, CYAN);     Takeoff(f1, 150);     Delay(6000)
AllOn(f1, PURPLE);   Move2(f1, 20, 20, 150); Delay(4000)
AllOn(f1, RED);      Rotation_Delta(f1, 360, 0, 0); Delay(5000)
AllOn(f1, GREEN);    Land(f1);             Delay(5000)

AllOff(f1)
Disarm(f1)
disconnect()