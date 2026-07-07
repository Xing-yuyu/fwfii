from fwfii.fc import *
from fwfii.fc.emergency import Emergency_Server
from fwfii.utils import *
from fwfii.led import *


s = Emergency_Server()
f1001 = Flight(71101)

Delay(500)
BodyOn(f1001, 0x0000ff, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0xffff00, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0x0000ff, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0xffff00, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0x0000ff, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0xffff00, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0x0000ff, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0xffff00, 1, emergency=True)
Delay(500)
BodyOn(f1001, 0x0000ff, 1, emergency=True)
Delay(500)
BodyOff(f1001, emergency=True)

Delay(500)
s.close()
