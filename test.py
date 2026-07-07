#!/usr/bin/env python

from gtrfs.fc import *

f1 = Flight(71101)

Move2(f1, 1, 2, 1, 0)

LED(f1, 0, 0, 0xff,
        -1, 0, 0,
        -1, 0, 0,
        -1, 0, 0, 1000)



Move2(f1, 2, 2, 1, 3000)



LED(f1, 0, 1, 0xff00,
        -1, 0, 0,
        -1, 0, 0,
        -1, 0, 0, 4000)
