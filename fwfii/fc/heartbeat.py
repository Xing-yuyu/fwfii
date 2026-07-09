#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread, Lock
import time
import traceback
import os
from fwfii.utils import *

class HeartBeat:
    INTERVAL = 0.2
    _enable = True
    flights = {}
    _lock = Lock()

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
        with HeartBeat._lock:
            HeartBeat.flights[flight.uavid] = flight

    @staticmethod
    def removeFlight(flight):
        with HeartBeat._lock:
            HeartBeat.flights.pop(flight.uavid, None)

    @staticmethod
    def addFlights(flights):
        with HeartBeat._lock:
            HeartBeat.flights.update(flights)

    def _beating_(self):
        from .advanced import HeartBeatData, RequestPosition, RequestBatteryCurrent
        while self._sending:
            time.sleep(0.001)
            if self._sending == False:
                break
            if HeartBeat._enable:
                # Snapshot to avoid "dictionary changed size during iteration"
                with HeartBeat._lock:
                    flights_snapshot = list(HeartBeat.flights.items())
                for uavid, flight in flights_snapshot:
                    time.sleep(0.01)
                    if uavid not in HeartBeat.flights:
                        continue
                    if GetCurTime() - flight.lastBeatTime >= self.INTERVAL:
                        HeartBeatData(flight)
                        RequestPosition(flight)
                        # Save position to file (compatible with non-Windows)
                        appData = os.getenv("APPDATA")
                        if appData:
                            pos_dir = appData + '/FlightPos'
                            if not os.path.exists(pos_dir):
                                os.makedirs(pos_dir, exist_ok=True)
                            try:
                                with open(pos_dir + '/' + str(uavid), 'w') as fp:
                                    fp.write(str(flight.position))
                            except Exception:
                                pass
                        # Print position with timestamp (ms) + battery % + fcstatus
                        now = time.time()
                        ms = int(now * 1000) % 1000
                        ts = time.strftime("%H:%M:%S", time.localtime(now))
                        ts = f"{ts}.{ms:03d}"
                        x, y, z, yaw = flight.position
                        # Battery: flight.voltage = direct percentage (0-100) from reg=8 payload[3]
                        bat_pct = flight.voltage if flight.voltage else 0
                        print(f"[{ts}] ID:{uavid} Pos:({x:.0f},{y:.0f},{z:.0f},{yaw:.0f}) Bat:{bat_pct}% [{flight.fcstatus}] {flight.flightmode}")
                        RequestBatteryCurrent(flight)
                        flight.lastBeatTime = GetCurTime()
        print("HeartBeat _beating_ end...\n")

    def close(self):
        try:
            self._sending = False
        except Exception:
            traceback.print_exc()
