#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM
import ctypes
import math
import traceback
from .advanced import Position, Attitude
from .flight import Flight
import time

class _VisualOdomData(ctypes.LittleEndianStructure):
    _fields_ = [ ("RigidNum",   ctypes.c_int32),
                 ("RigidId",    ctypes.c_int32),
                 ("pos_X",      ctypes.c_float),
                 ("pos_Y",      ctypes.c_float),
                 ("pos_Z",      ctypes.c_float),
                 ("q0",         ctypes.c_float),
                 ("q1",         ctypes.c_float),
                 ("q2",         ctypes.c_float),
                 ("q3",         ctypes.c_float)]
                 
    def __init__(self, s):
        pass
        
    def __new__(cls, buf):
        return cls.from_buffer_copy(buf)    

    def __str__(self):
        return ''.join('{:d} '.format(x) for x in [self.RigidNum, self.RigidId]) + \
               ''.join('{:f} '.format(x) for x in [self.pos_X, self.pos_Y, self.pos_Z, self.q0, self.q1, self.q2, self.q3])
        

class VisualOdom:
    bufferSize = ctypes.sizeof(_VisualOdomData)
    vo = None
    def __init__(self, enable = False, port = 9753):
        self.dumping = True
        self.t = None
        self._avalible = False
        try:
            if enable:
                self.port = port
                self.conn = socket(AF_INET, SOCK_STREAM)
                self.conn.settimeout(2.0)
                self.conn.connect(("localhost", port)) # DO NOT remove the ()
                self._avalible = True
                self.t = Thread(target = self.__dumping__, args=())
                self.t.start()
        except Exception:
            self._avalible = False
            traceback.print_exc()
            print("Cannot connect to odom")

    def avalible(self):
        return self._avalible
        
    def _quart2euler(self, q0, q1, q2, q3):
        roll  = math.atan2((2 * (q0 * q1 + q2 * q3)), (1 - 2 * (q1 ** 2 + q2 ** 2)))
        pitch = math.asin(2 * (q0 * q2 - q3 * q1))
        yaw   = math.atan2((2 * (q0 * q3 + q1 * q2)), (1 - 2 * (q2 ** 2 + q3 ** 2)))
        return pitch, roll, yaw
        
    def __dumping__(self):
        msg = ""
        expected_bytes = self.bufferSize
        while self.dumping:
            time.sleep(0.001)
            try:
                #print("&&&&&&&&&&&&&&&&&&&&&&&&&")
                msg += self.conn.recv(expected_bytes) 
                recvd_bytes = len(msg)
                if recvd_bytes < self.bufferSize:
                    expected_bytes = expected_bytes - recvd_bytes
                    continue
                self.vo = _VisualOdomData(msg)
                msg = ""
                expected_bytes = self.bufferSize
                print('[O<] ' + str(self.vo))

                Position(Flight(self.vo.RigidId), int(self.vo.pos_X * 10), int(self.vo.pos_Y * 10), int(self.vo.pos_Z * 10))
                pitch, roll, yaw = self._quart2euler(self.vo.q0, self.vo.q1, self.vo.q2, self.vo.q3)
                Attitude(Flight(self.vo.RigidId), int(pitch * 10000), int(roll * 10000), int(yaw * 10000))
            except Exception:
                #traceback.print_exc()
                pass

        print("VisualOdom __dumping__ end...\n")

    def send(self, bytes):
        try:
            self.conn.send(bytes)
        except Exception:
            traceback.print_exc()
            self.conn.close()
            self.conn = socket(AF_INET, SOCK_STREAM)
            self.conn.settimeout(2.0)
            self.conn.connect(("localhost", self.port)) # DO NOT remove the ()
            self.send(bytes)

    def close(self):
        try:
            if self.t != None:
                self.dumping = False
                self.t.join()
            self.conn.close()
        except Exception:
            traceback.print_exc()

'''               
if __name__ == '__main__':
    vo = VisualOdom()
    #self.vo = VisualOdomData("@@#$@#%@#%@#$#@$#@$%@#%@#%@#%#@%#@%#@%#@%")
    #print self.vo.RigidNum, self.vo.RigidId, self.vo.pos_X, self.vo.pos_Y, self.vo.pos_Z, self.vo.q0, self.vo.q1, self.vo.q2, self.vo.q3 
'''