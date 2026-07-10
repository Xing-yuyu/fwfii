"""
紧急停机 - 立刻停止所有电机
"""
from fwfii.fc import Flight, Land

# 修改为你的无人机 ID
DRONE_ID = 71101

print("紧急降落！")
Land(Flight(DRONE_ID), emergency=True)
print("已发送降落指令")