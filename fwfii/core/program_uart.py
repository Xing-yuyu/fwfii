#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.atom import AtomDelivery as delivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc.odom import VisualOdom as odom
from fwfii.fc.emergency import Emergency_Server as server
from multiprocessing.connection import Listener
import traceback
from threading import Thread 

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description = 'Goertek Roboticks Formation System - Zigbee mode')
    parser.add_argument('serial_port', help = 'the serial port you want to open')
    parser.add_argument('script', help = 'your own formation script')
    args = parser.parse_args()
    
    #
    # Receiving Odometry data from optical track
    #
    o = odom()
    #
    # Sending HeatBeat packet
    #
    h = HeartBeat()
        
    #
    # transport the atoms to flight control over serial port
    #
    d = delivery(args.serial_port, o)
    
    #
    # Server for emergency command sending
    #
    s = server()
    
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
    h.close()
    s.close()
    o.close()
    d.close()

if __name__ == '__main__':
    main()
    