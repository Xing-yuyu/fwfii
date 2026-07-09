"""
紧急停机 - 立刻停止所有电机
"""
from fwfii.fc import Flight, Stop

# 修改为你的无人机 ID
DRONE_ID = 71101

print("紧急停机！")
Stop(Flight(DRONE_ID), emergency=True)
print("已发送停机指令")