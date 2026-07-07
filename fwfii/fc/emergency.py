#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from threading import Thread
from multiprocessing.connection import Client, Listener
import traceback
from fwfii.atom import AtomRepo as repo
from fwfii.atom import zigbeePack, crc, wifiPack, flightPayload
import ctypes
import time

class Emergency_Server:
    def __init__(self):
        self.serving = True
        self.t = Thread(target = self._echo_server, args=(('', 25000), b'peekaboo'))
        self.t.start()
                
    def _echo_server(self, address, authkey):
        self.serv = Listener(address, authkey=authkey)
        while self.serving:
            #time.sleep(0.001)
            try:
                client = self.serv.accept()
                self._echo_client(client)
            except Exception:
                traceback.print_exc()

        print("Emergency_Server _echo_server end...\n")
                
    def _echo_client(self, conn):
        try:
            while self.serving:
                #time.sleep(0.001)
                msg = conn.recv()
                # print("[E]> " + repr(msg))
                # Adapted the Zigbee mechenism
                zigbeemsg = (zigbeePack).from_buffer_copy(msg)
                wifimsg = (wifiPack).from_buffer_copy(zigbeemsg.payload)
                if wifimsg.pack_header.reg == 150:
                    fp = (flightPayload).from_buffer_copy(wifimsg.payload)
                    from fwfii.fc import HeartBeat
                    if fp.x == 1:
                        # enable heartbeat
                        HeartBeat.Enable()
                    else:
                        # disable heartbeat
                        HeartBeat.Disable()
                elif wifimsg.pack_header.reg == 151:
                    '''
                    To save the current pos by generating a temporary file, which is feeded to 
                    '''
                    fp = (flightPayload).from_buffer_copy(wifimsg.payload)
                    from fwfii.fc import Monitor
                    Monitor.SavePos(fp.x)
                else:
                    zigbeePack.COUNTER += 1
                    zigbeemsg.zigbee_header.counter = zigbeePack.COUNTER
                    zigbeemsg.crc = crc((ctypes.c_uint8 * ctypes.sizeof(zigbeemsg)).from_buffer_copy((zigbeemsg))[1 : ctypes.sizeof(zigbeemsg) - 1]) 
                    repo.storage(zigbeemsg)
        except EOFError:
            pass
            #print('Connection closed')
                
    def close(self, test = 0):
        try:
            self.serving = False
            # 运行一下client端连接，保证Emergency_Server Listener的accept退出阻塞
            c = Emergency_Client()
            self.serv.close()
            self.t.join()
        except Exception:
            traceback.print_exc()

        
class Emergency_Client:

    conn = 0

    @staticmethod
    def send(payload):
        tryCnt = 3
        while not Emergency_Client.conn:
            try:
                tryCnt -= 1
                Emergency_Client.conn = Client(('localhost', 25000), authkey=b'peekaboo')
            except:
                if tryCnt <= 0:
                    print("Need connect flight first")
                    break
                continue
            #print("Emergency_Client connect")
            
        Emergency_Client.conn.send(payload)