"""
LED 灯测试 - 验证通信链路
运行此脚本前需先用原版软件连接一次无人机
"""
from fwfii.fc import Flight
from fwfii.fc.emergency import Emergency_Server
from fwfii.led import BodyOn, BodyOff
from fwfii.utils import Delay

DRONE_ID = 71101

s = Emergency_Server()
f1 = Flight(DRONE_ID)

# 蓝灯闪烁 3 次
for _ in range(3):
    BodyOn(f1, 0x0000ff, 1, emergency=True)
    Delay(300)
    BodyOff(f1, emergency=True)
    Delay(300)

s.close()
print("LED 测试完成")