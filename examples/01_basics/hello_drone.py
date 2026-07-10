"""
40×40 定位毯 — 起飞悬停降落 + 灯光
====================================
uavid: 71101  定位毯: 40×40cm
安全限制: XY 5~35cm | Z ≤ 80cm | 低速
"""
from fwfii.quick import connect, disconnect
from fwfii.fc import *
from fwfii.fc.advanced import *
from fwfii.led.lamp import AllOn, AllBlink, AllBreath, AllOff
from fwfii.utils import Delay

# ============ 配置 ============
DRONE_ID = 71101
INIT_POS = (5, 5, 0, 0)      # 原点设为毯子中心

# 颜色
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF
YELLOW = 0xFFFF00
WHITE = 0xFFFFFF

def main():
    print("=" * 45)
    print("  40×40 定位毯 | 71101 | 起飞悬停测试")
    print("=" * 45)

    # 1. 连接
    d, h, f1 = connect(DRONE_ID)
    f1.set_init_pos(INIT_POS[0], INIT_POS[1])  # 毯子中心

    # 2. 设置
    ProgrammingMode(f1)
    Delay(500)
    MaxVelXY(f1, 50)           # 低速
    MaxVelZ(f1, 30)
    MaxAccXY(f1, 200)
    MaxAccZ(f1, 200)

    # 3. 解锁 → 蓝灯闪
    AllBlink(f1, BLUE, 300, 300)
    Arm(f1)
    Delay(2000)

    # 4. 起飞 → 绿灯呼吸, 飞到 60cm
    print("[起飞 → 60cm]")
    AllBreath(f1, GREEN, 600, 600)
    Takeoff(f1, 100)
    Delay(4000)

    # 5. 悬停 → 金色常亮
    print("[悬停 @ 60cm]")
    AllOn(f1, YELLOW)
    Delay(2000)

    # 6. 上升 → 白色
    print("[上升 → 80cm]")
    AllOn(f1, WHITE)
    Move2(f1, 5, 5, 150)
    Delay(3000)

    # 7. 下降 → 红色呼吸
    print("[下降 → 60cm]")
    AllBreath(f1, RED, 600, 600)
    Move2(f1, 5, 5, 100)
    Delay(2000)

    # 8. 降落
    print("[降落]")
    AllBlink(f1, YELLOW, 300, 300)
    Land(f1)
    Delay(5000)

    # 9. 上锁 → 灭灯
    AllOff(f1)
    Disarm(f1)
    Delay(1000)

    disconnect()
    print("\n测试完成!")

if __name__ == "__main__":
    main()
