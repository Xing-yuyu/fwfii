"""紧急停机"""
from fwfii.fc import Flight, Stop
DRONE_ID = 71101
Stop(Flight(DRONE_ID), emergency=True)
print("停机指令已发送")