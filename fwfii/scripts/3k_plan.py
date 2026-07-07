#! /usr/bin/env python

from fwfii.fc import *

f1 = Flight(1001)

ts = 0

while True:
    Move2(f1, 1, 2, 1, ts)

    ts += 1
    if ts >= 32:
        break
        