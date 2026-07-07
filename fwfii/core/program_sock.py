#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.atom import UdpDelivery, TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc.monitor import Monitor
from fwfii.fc.odom import VisualOdom as odom
from fwfii.utils import Delay
from fwfii.fc.emergency import Emergency_Server as server
from multiprocessing.connection import Listener
import traceback
from threading import Thread 
import signal
import os
import ast

def signal_handler(signum, frame):
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)
    import curses
    curses.endwin()
    
def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description = 'Goertek Roboticks Formation System - wifi mode')
    parser.add_argument('script', help = 'your own formation script')
    parser.add_argument('-m', '-monitor', dest='monitor', nargs = "?", default = False, type = ast.literal_eval, help = 'show information')
    parser.add_argument('-p', '-protocol', dest='protocol', nargs = '?', default = 'tcp', help = 'udp or tcp')
    parser.add_argument('-o', '-optical_track', dest='optical_track', nargs = "?", default = False, type = ast.literal_eval, help = 'optical track enabled')
    args = parser.parse_args()
    
    #
    # Receiving Odometry data from optical track
    #
    o = odom(enable = args.optical_track)
    #
    # Sending HeatBeat packet
    #
    h = HeartBeat()
   
    #
    # transport the atoms to flight control over serial port
    #
    if args.protocol == 'udp':
        d = UdpDelivery(o)
    else:
        d = TcpDelivery(o)

    if args.monitor:
        print("Press [q] to quit the dashboard, and press [m] to get back\n")
        m = Monitor()
    
    #
    # Server for emergency command sending
    #
    s = server()

    signal.signal(signal.SIGINT, signal_handler)
    
    #
    # Run the formation scripts
    #
    try:
        f = open(args.script)
        script = f.read()
        f.close()
        exec(script)
    except Exception:
        traceback.print_exc()
    
    #
    # Quit
    #
    if args.monitor:
        m.close()
    h.close()
    s.close()
    o.close()
    d.close()  

if __name__ == '__main__':
    main()
    