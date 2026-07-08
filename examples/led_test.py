"""LED 测试 - 彩虹闪烁"""
from fwfii.quick import connect, disconnect
from fwfii.led.lamp import AllOn, AllOff
from fwfii.utils import Delay

DRONE_ID = 71101
COLORS = [0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF, 0x0000FF, 0xFF00FF]

d, h, f1 = connect(DRONE_ID)

for c in COLORS:
    AllOn(f1, c); Delay(500)

AllOff(f1)
disconnect()