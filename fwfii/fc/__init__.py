#!/usr/bin/env python
from __future__ import division, absolute_import, print_function

from .flight import Flight
from .advanced import *
from .basic import * 
from .heartbeat import *


def __getattr__(name):
    if name == "Monitor":
        from .monitor import Monitor

        return Monitor
    if name == "VisualOdom":
        from .odom import VisualOdom

        return VisualOdom
    raise AttributeError("module 'fwfii.fc' has no attribute {!r}".format(name))
