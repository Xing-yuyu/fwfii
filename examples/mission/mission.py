"""
离线任务脚本 - 配合 mission_upload.py 使用
编译→上传后，无人机会按时间戳自主执行
"""
from fwfii.fc import *
from fwfii.utils import *

f1 = Flight(71101)

Arm(f1, ts=100)
Takeoff(f1, 120, ts=1100)
Forward(f1, 50, ts=3100)
Right(f1, 50, ts=6100)
Backward(f1, 50, ts=9100)
Left(f1, 50, ts=12100)
Land(f1, ts=15100)
Disarm(f1, ts=17100)