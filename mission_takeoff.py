from gtrfs.fc import *
from gtrfs.utils import Delay

f1 = Flight(1001)

ProgrammingMode(f1, emergency=True)
Delay(2000)
# Take off to 100cm
Land(f1, emergency=True)
