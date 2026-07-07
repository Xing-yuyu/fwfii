#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread
import time
import traceback
import os
from fwfii.utils import *

class HeartBeat:
    INTERVAL = 0.2
    _enable = True
    flights = {}
    def __init__(self):
        self._sending = True
        self.t = Thread(target = self._beating_, args = ())
        self.t.start()
        
    @staticmethod
    def Enable():
        HeartBeat._enable = True

    @staticmethod
    def Disable():
        HeartBeat._enable = False

    @staticmethod
    def Show(enable):
        HeartBeat._showing = enable

    @staticmethod
    def addFlight(flight):
        HeartBeat.flights[flight.uavid] = flight

    @staticmethod
    def removeFlight(flight):
        HeartBeat.flights.pop(flight.uavid, None)
        
    @staticmethod
    def addFlights(flights):
        HeartBeat.flights += flights

    def _beating_(self):
        from .advanced import HeartBeatData, RequestPosition, RequestBatteryCurrent
        while self._sending:
            time.sleep(0.001)
            if self._sending == False:
                break
            if HeartBeat._enable:
                for uavid, flight in self.flights.items():
                    time.sleep(0.01)
                    if GetCurTime() - flight.lastBeatTime >= self.INTERVAL:
                        HeartBeatData(flight)
                        RequestPosition(flight)
                        appData = os.getenv("APPDATA")
                        if not os.path.exists(appData + '/FlightPos'):
                            os.mkdir(appData + '/FlightPos')
                        fp = open(appData + '/FlightPos/' + str(uavid), 'w')
                        fp.write(str(flight.position))
                        #fp.write(str(flight.position) + '\n')
                        fp.close()
                        print(flight.position)
                        RequestBatteryCurrent(flight)
                        flight.lastBeatTime = GetCurTime()
                    #time.sleep(self.INTERVAL)
                    #time.sleep(self.INTERVAL / len(self.flights) - (time.clock() - ct))
                    #print("*****************************_beating_")
        print("HeartBeat _beating_ end...\n")
        
    

    def close(self):
        try:
            self._sending = False
            self.t.join()                
        except Exception:
            traceback.print_exc()