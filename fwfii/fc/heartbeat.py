#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread
import time
import traceback
import threading
from fwfii.utils import *

class HeartBeat:
    INTERVAL = 0.2
    _enable = True
    flights = {}
    _lock = threading.RLock()

    def __init__(self, interval=None):
        self.INTERVAL = interval or HeartBeat.INTERVAL
        self._sending = True
        self.errors = []
        self.t = Thread(target = self._beating_, args = (), daemon=True)
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
        with HeartBeat._lock:
            HeartBeat.flights[flight.uavid] = flight

    @staticmethod
    def removeFlight(flight):
        with HeartBeat._lock:
            HeartBeat.flights.pop(flight.uavid, None)
        
    @staticmethod
    def addFlights(flights):
        with HeartBeat._lock:
            HeartBeat.flights.update({flight.uavid: flight for flight in flights})

    def _beating_(self):
        from .advanced import HeartBeatData, RequestPosition, RequestBatteryCurrent
        while self._sending:
            time.sleep(0.01)
            if not HeartBeat._enable:
                continue
            with HeartBeat._lock:
                flights = list(HeartBeat.flights.items())
            for _uavid, flight in flights:
                if not self._sending:
                    break
                try:
                    if GetCurTime() - flight.lastBeatTime >= self.INTERVAL:
                        HeartBeatData(flight)
                        RequestPosition(flight)
                        RequestBatteryCurrent(flight)
                        flight.lastBeatTime = GetCurTime()
                except Exception as exc:
                    self.errors.append(exc)
                    traceback.print_exc()

    def close(self):
        try:
            self._sending = False
            self.t.join(timeout=2)
        except Exception:
            traceback.print_exc()
