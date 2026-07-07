from gtrfs.fc.emergency import Emergency_Server
from gtrfs.fc import Flight
from gtrfs.led import BodyOn, BodyOff
from gtrfs.utils import Delay

s = Emergency_Server()
f1 = Flight(71101)

Delay(500)
BodyOn(f1, 0x0000ff, 1, emergency=True)
Delay(500)
BodyOff(f1, emergency=True)

s.close()