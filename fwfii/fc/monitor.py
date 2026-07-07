#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread
import time
from .heartbeat import HeartBeat
from fwfii.utils import Delay, clear, GetCurTime
import traceback

class Monitor: 
    _savepos = False
    def __init__(self):
        self._showing = True
        self._dashboard = True
        self._plot = False
        self.s = Thread(target = self._showstatus_, args = ())
        self.s.start()

    @staticmethod
    def SavePos(b):
        Monitor._savepos = b

    def _showstatus_(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.cm as cm
        import numpy as np
        import curses
        import os
        import subprocess
        
        screen = curses.initscr()
        screen.nodelay(True)
        curses.noecho()
        curses.cbreak()
        #my_window = curses.newwin(50, 20, 0, 0)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        
        loop_count = 0
        while self._showing:
            time.sleep(0.001)
            ct = GetCurTime()
            xs = []
            ys = []
            zs = []
            info = {}
            for uavid, flight in HeartBeat.flights.items():
                info[uavid] = flight.printInfo()
                xs += [info[uavid][3]]
                ys += [info[uavid][4]]
                zs += [info[uavid][5]]

            if len(info) > 0:
                if self._plot:
                    colors = cm.rainbow(np.linspace(0, 1, len(ys)))
                    ax.cla()
                    for x, y, z, c in zip(xs, ys, zs, colors):
                        ax.scatter(x, y, z, color = c, marker='o')
                table = pd.DataFrame.from_dict(info, orient = "index", \
                    columns = ["flightmode", "voltage", "gpsstatus", "fcstatus", "x", "y", "z", "yaw", \
                            "maporigin"])
                #clear()
                print(time.strftime("%H:%M:%S:"))
                print(table.sort_index())
                filename = 'dashboard' + time.strftime("%y%m%d") + '.log'
                log = open(filename, "a")
                log.write(time.strftime("%H:%M:%S:") + "\n")
                log.write(str(table.sort_index()))
                log.write("\r\n")
                loop_count = loop_count + 1
                if  0 == (loop_count % 60):
                    log.close()
                
                c = screen.getch()
                if c == ord('q') and self._dashboard:
                    curses.endwin()
                    self._dashboard = False
                elif c == ord('m') and not self._dashboard:
                    self._dashboard = True
                elif c == ord('p') and not self._plot:
                    self._plot = True
                    
                if self._dashboard:
                    screen.addstr(0, 0, time.strftime("%H:%M:%S:") + "\n" + str(table.sort_index()))
                    screen.refresh()

                if Monitor._savepos:
                    print("generate new pos file")
                    pos = np.array(table.values[:, 3 : 6].transpose(), dtype = float)
                    pos = pos * 0.01
                    pos[2, :] += 5
                
                    #print(pos.dtype)
                    #print(pos)
                    np.savez("pos.npz", points = pos)
                    Monitor._savepos = False
                if self._plot:
                    plt.pause(1)
                else:
                    time.sleep(1)
            else:
                time.sleep(1)

    @staticmethod
    def saveposition():
        Monitor._savepos = True

    def close(self):
        import curses
        self._showing = False
        curses.endwin()
        self.s.join()