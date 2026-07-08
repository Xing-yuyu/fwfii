"""紧急降落"""
from fwfii.quick import connect, disconnect
from fwfii.fc import Land
DRONE_ID = 71101
d, h, f1 = connect(DRONE_ID)
Land(f1)
disconnect()