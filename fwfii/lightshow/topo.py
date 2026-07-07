#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.fc import Reach, Flight, SetOrigin
from math import cos, sin, pi
from numpy import array, zeros, nonzero

class TopoMaker:
    '''
    3-D numpy array
    '''
    LOCATION_SCALING_FACTOR = 1.1131884502145034

    def __init__(self, origin, xlength, ylength, unit = 1, yaw = 0):
        self._origin = origin
        self._unit = unit
        self._tnb = array([[cos(yaw), -sin(yaw), 0], 
                           [sin(yaw),  cos(yaw), 0], 
                           [0, 0, 1]])
        self.map = zeros((ylength, xlength), dtype = int)                           

    def longitude_scale(self, lat):
        scale = cos(lat * 1.0e-7 * pi / 180.0)
        if scale < 0.01:
            scale = 0.01
        elif scale > 1.0:
            scale = 1.0
        return scale

    def XYZ2NED(self, x, y, z):
        origin_lat = self._origin[0] * 1e7
        origin_lng = self._origin[1] * 1e7
        origin_alt = self._origin[2]

        lat = x / self.LOCATION_SCALING_FACTOR + origin_lat
        lng = y / self.LOCATION_SCALING_FACTOR / self.longitude_scale(origin_lat) + origin_lng
        alt = z + origin_alt

        return (lat, lng, alt)

    def addCopter(self, id, xindex, yindex):
        ylength = self.map.shape[0]
        self.map[ylength - 1 - yindex, xindex] = id
        #self.setOrigin(id)

    def showMap(self):
        print(self.map)

    def setOrigin(self, id):
        '''
        Set the HOME in the topo coordinate
        '''
        SetOrigin(Flight(id), int(self._origin[0] * 1e7), int(self._origin[1] * 1e7), emergency = False)
        

    def moveCopter(self, id, x, y, z, ts = 0, emergency = False, timeout = 0):
        Reach(Flight(id), x, y, z, ts, emergency, timeout)
        return (x, y, z)

'''
if __name__ == '__main__':
    pass
'''