from fwfii.fc import *
from fwfii.fc.emergency import Emergency_Server
from fwfii.utils import Delay

# 1. 启动 Emergency 服务器
s = Emergency_Server()
Delay(500)

# 2. 创建无人机
f1 = Flight(71101)

# 3. 切换到编程模式
ProgrammingMode(f1, emergency=True)
Delay(2000)

# 4. 解锁
Arm(f1, emergency=True)
Delay(2000)

# 5. 起飞
Takeoff(f1, 120, emergency=True)
Delay(5000)

# 6. 移动
Move2(f1, 20, 40, 100, emergency=True)
Delay(5000)

# 7. 降落
Land(f1, emergency=True)
Delay(5000)

# 8. 关闭
s.close()