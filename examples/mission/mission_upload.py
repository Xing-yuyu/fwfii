"""
离线任务上传 - 编译→上传→起飞
"""
from fwfii.quick import connect, disconnect, plan, deliver, mission_start

# 1. 编译（自动断开连接）
plan('mission.py', './output')

# 2. 上传
deliver(71101, './output')

# 3. 重连心跳
connect(71101)

# 4. 倒计时起飞
mission_start([71], countdown=5)