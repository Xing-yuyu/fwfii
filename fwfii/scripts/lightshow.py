from fwfii.fc import *
from fwfii.lightshow import *
from fwfii.utils import *

origin_lat = 36.10823
origin_lng = 120.475354
origin_alt = 0

id = 1001

f1 = Flight(1001)
t  = TopoMaker((origin_lat, origin_lng, origin_alt))
#Arm(f1)
#Delay(500)
#Takeoff(f1, 200)
#TurnOn(f1, 0xFF00FF)
#Delay(5000)

t.moveCopter(id, 2, 0, 500, 0)


#Delay(5000)

#Land(f1)
#Delay(10000)
#Disarm(f1)

