#!/usr/bin/env python
from fwfii.fc import Flight
from fwfii.led import *
from fwfii.utils import Delay

f = Flight(71101)

TurnOnSingle(f, 4, 0xFF0000)
Delay(2000)
TurnOnSingle(f, 10, 0x00FF00)
Delay(2000)
TurnOffSingle(f, 10)
Delay(2000)
TurnOnMulti(f, [1, 3, 5, 7 , 9, 11], \
                    [0x485323, \
                     0x346390, \
                     0xAAEEDD, \
                     0xFF33FF, \
                     0x00FFFF, \
                     0x2200AA])

Delay(2000)
TurnOffMulti(f, [1, 3, 5, 7, 9, 11])                            
Delay(2000)
TurnOnAll(f, [0xFF0000, \
                   0x00FF00, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF])  

Delay(2000)
TurnOffAll(f)
Delay(2000)
BlinkSingle(f, 10, 0xFF0000)
Delay(10000)
TurnOffAll(f)
Delay(2000)
BlinkFastAll(f, [0xFF0000, \
                   0x00FF00, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF]) 
Delay(10000)
TurnOffAll(f)
Delay(2000)
BlinkSlowAll(f, [0xFF0000, \
                   0x00FF00, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF]) 

Delay(10000)
TurnOffAll(f)
Delay(2000)
Breath(f, [1, 3, 5, 7 , 9, 11], \
                    [0x485323, \
                     0x346390, \
                     0xAAEEDD, \
                     0xFF33FF, \
                     0x00FFFF, \
                     0x2200AA])     
Delay(5000)
TurnOffAll(f)
Delay(2000)                     

HorseRace(f, [0xFF0000, \
                   0x00FF00, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF, \
                   0x0000FF])

Delay(5000)
TurnOffAll(f)
                    