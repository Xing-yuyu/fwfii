#! /usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread
import traceback
from .image import ImageReader
from fwfii.lightshow import light
from fwfii.utils import Delay
from fwfii.atom import AtomRepo
from fwfii.lightshow import TurnOn

class FrameMaker:
    def __init__(self):
        self._ids = AtomRepo._fifo

    def addFrame(self, pixels, ts):
        '''
        pixels, a rgb birmap described by numpy
        ts, timestamp
        '''
        colors = pixels.flatten()
        for idx, flight in enumerate(self._ids):
            TurnOn(flight, colors[idx], ts)

    def addImage(self, filename, ts):
        '''
        filename, the gif filename, support GIF, PNG, JPG ...
        ts, timestamp
        '''
        ani = ImageReader(filename)
        while True:
            pixels, eof = ani.extractPixels()
            # TODO, currently set 30 fps
            self.addFrame(pixels, ts)
            if '.gif' in filename:
                Delay(30)
            if eof:
                break

'''
if __name__ == '__main__':
    pass
'''