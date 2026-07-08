#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from collections import namedtuple
from threading import Thread
import socket
import ctypes
import time
import traceback
from .repo import AtomRepo
from .gen import uavPack, wifiPack
from fwfii.utils import GetCurTime

class AtomDelivery:
    bufferSize = ctypes.sizeof(uavPack)
    
    def __init__(self, port, vo = None):
        try:
            import serial
            self._handle_ = serial.Serial(port, 115200, rtscts = True, timeout = 2)
            self._sending = True
            self._receiving = True
            self._pause_sending = False
            self.vo = vo
            self.atom = None
            self.INTERVAL = 0.2
            self.s = Thread(target = self.__sending__, args=(), daemon=True)
            self.r = Thread(target = self.__receiving__, args=(), daemon=True)
            self.s.start()
            self.r.start()
        except Exception:
            traceback.print_exc()
        
    def __sending__(self):
        while self._sending:
            time.sleep(0.001)
            try:
                if self._pause_sending:
                    continue

                ct = GetCurTime()
                try:
                    self.atom = AtomRepo.getNext(timeout=0.05)
                except AtomRepo.Empty:
                    continue

                #print("[S]> " + repr(self.atom))
                #print "[S]> ", ct
                self.writebytes((self.atom))
                while GetCurTime() - ct < self.INTERVAL:
                    time.sleep(0.001)
                    pass
            except Exception:
                traceback.print_exc()

        print("AtomDelivery __sending__ end...\n")
        
    def __receiving__(self):
        msg = b""
        expected_bytes = self.bufferSize
        while self._receiving:
            time.sleep(0.001)
            try:  
                msg = self._readbytes(expected_bytes)
                state = (uavPack).from_buffer_copy(msg)
                if (state.zigbee_header.id == 0xdd):
                    group = state.zigbee_header.group
                    id    = state.zigbee_header.address
                    from fwfii.fc import HeartBeat
                    uavid = (group * 1000 + id)

                    if uavid in HeartBeat.flights.keys():
                        if (state.reg == 22):
                            z = state.payload[0] + (state.payload[1] << 8) + (state.payload[2] << 16)
                            if z & 0x800000:
                                z = -(-0x1000000 + z)
                            else:
                                z = -z
                            x = ctypes.c_int32(state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)).value
                            y = ctypes.c_int32(state.payload[7] + (state.payload[8] << 8) + (state.payload[9] << 16) + (state.payload[10] << 24)).value
                            yaw = state.payload[11] + (state.payload[12] << 8)
                            HeartBeat.flights[uavid].position = (x, y, z, yaw)
                        elif (state.reg == 4):
                            #print("[R]< " + repr(state))
                            HeartBeat.flights[uavid].obtainStatus(state.payload)
                        elif (state.reg == 100):
                            lat = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                            lng = state.payload[7] + (state.payload[8] << 8) + (state.payload[9] << 16) + (state.payload[10] << 24)
                            #HeartBeat.flights[uavid].setMapOrigin(lat, lng)
                            HeartBeat.flights[uavid].maporigin = (lat, lng)
                        elif (state.reg == 101):
                            utc = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                            #HeartBeat.flights[uavid].setUTC(utc)
                            HeartBeat.flights[uavid].launchutc = utc
                        elif (state.reg == 102):
                            lat = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                            lng = state.payload[7] + (state.payload[8] << 8) + (state.payload[9] << 16) + (state.payload[10] << 24)
                            alt = state.payload[11] + (state.payload[12] << 8) + (state.payload[13] << 16)
                            #HeartBeat.flights[uavid].setBase(lat, lng, alt)
                            HeartBeat.flights[uavid].rtkbaseloc = (lat, lng, alt)
                if self.vo and self.vo.avalible():
                    self.vo.send((state))
                msg = b""
                expected_bytes = self.bufferSize
            except Exception:
                if self.vo and self.vo.avalible():
                    traceback.print_exc()
                else:
                    pass

        print("AtomDelivery __receiving__ end...\n")
                
    
    def _readbytes(self, count):
        return self._handle_.read(count)
        
    def writebytes(self, buf):
        return self._handle_.write(buf)

    def pause(self):
        self._pause_sending = True

    def resume(self):
        self._pause_sending = False

    def close(self):
        try:
            self._sending = False
            self._receiving = False
            self._connecting = False
            if hasattr(self, 's'):
                self.s.join(timeout=2)
            if hasattr(self, 'r'):
                self.r.join(timeout=2)
            if hasattr(self, 'c'):
                self.c.join(timeout=2)
            if hasattr(self, 'client'):
                for client in list(self.client.values()):
                    try:
                        client.shutdown(socket.SHUT_RDWR)
                        client.close()
                    except:
                        pass
            if hasattr(self, '_handle_'):
                try:
                    self._handle_.close()
                except:
                    pass
        except Exception:
            traceback.print_exc()

class TcpDelivery(AtomDelivery):
    def __init__(self, vo):
        self.client = {}
        self.server = {}
        self.connect_threads = {}
        self.cache = {}
        self._sending = True
        self._receiving = True
        self._connecting = True
        self._pause_sending = False
        self.vo = vo
        self.atom = None
        self.INTERVAL = 0.2
        self.s = Thread(target = self.__sending__, args=(), daemon=True)
        self.r = Thread(target = self.__receiving__, args=(), daemon=True)
        self.s.start()
        self.r.start()


    def _notification(self, destaddr, result):
        if self.vo and self.vo.avalible():
            from fwfii.fc import ConnectionStatus
            ip = destaddr[0].split('.')
            flight = namedtuple('flight', ['uavid'])
            status = ConnectionStatus(flight(int(ip[2]) * 1000 + int(ip[3])), result)
            self.vo.send(status)

        if result:
            print("[Info]: connect to {} established".format(destaddr[0]))
        else:
            print("[Err]: connect to {} failed".format(destaddr[0]))
            
    def __connectServeritem__(self, destaddr, atom):
        while self._connecting and destaddr in self.server.keys():
            if not self.server[destaddr][0]:
                sock = None
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sock.settimeout(1)
                    print("Try to connect:" + repr(destaddr[0])) 
                    sock.connect(destaddr)
                    self._notification(destaddr, 1)
                    #sock.setblocking(0)
                    self.client[destaddr] = sock
                    self.server[destaddr] = (True, None)
                    self.writebytes(destaddr, atom)
                except Exception:
                    if sock is not None:
                        sock.close()
                    #traceback.print_exc()
                    self._notification(destaddr, 0)
            else:
                time.sleep(0.1)

    @staticmethod
    def disconnectnotification(destaddr):
        from fwfii.fc import HeartBeat
        addr = destaddr[0].split('.')
        uavid = int(addr[2]) * 1000 + int(addr[3])
        HeartBeat.flights[uavid].fcstatus = "N/A" 
        HeartBeat.flights[uavid].flightmode = "N/A"
        HeartBeat.flights[uavid].gpsstatus = "NO_GPS"
        #HeartBeat.flights[uavid].reset()
        

    def __sending__(self):
        while self._sending:
            #time.sleep(0.001)
            try:
                if self._pause_sending:
                    time.sleep(0.05)
                    continue
                
                try:
                    zigbeepack = AtomRepo.getNext(timeout=0.05)
                except AtomRepo.Empty:
                    continue
                self.atom = zigbeepack  
                #print("[zigbeepack] {}\n".format(zigbeepack.payload[6]))
                if zigbeepack.payload[6] == 124:
                    print("python send 124\n")
                    if self.vo and self.vo.avalible():
                        zigbeepack.payload[0]=0xdd
                        zigbeepack.payload[1]=0x13
                        zigbeepack.payload[21]=0xf3
                        self.vo.send(zigbeepack.payload)
                        continue
                if zigbeepack.payload[6]== 125:
                    print("python send 125 \n") 
                    if self.vo and self.vo.avalible():
                        zigbeepack.payload[0]=0xdd
                        zigbeepack.payload[1]=0x13
                        zigbeepack.payload[21]=0x46
                        self.vo.send(zigbeepack.payload)
                        continue
        
                if zigbeepack.zigbee_header.address == 255:
                    localaddr = ('0.0.0.0', 10013)
                    destaddr = ('192.168.{}.255'.format(zigbeepack.zigbee_header.group), 10012)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    sock.bind(localaddr)
                    sock.sendto(self.atom, destaddr)
                    sock.close()
                else:
                    destaddr = ('192.168.{}.{}'.format(zigbeepack.zigbee_header.group, zigbeepack.zigbee_header.address), 10014)
                    if destaddr not in self.server.keys():
                        if destaddr in self.connect_threads.keys() \
                        and not self.connect_threads[destaddr].is_alive():
                            self.connect_threads.pop(destaddr, None)
                        if destaddr not in self.connect_threads.keys():
                            #print("[S]Add> " + repr(destaddr))
                            self.server[destaddr] = (False, zigbeepack)
                            cthread = Thread(target = self.__connectServeritem__, args=(destaddr, zigbeepack,), daemon=True)
                            cthread.start()
                            self.connect_threads[destaddr] = cthread
                    elif self.atom != None:
                        #print "[S]> ", ct
                        self.writebytes(destaddr, self.atom)  
                
            except Exception:
                traceback.print_exc()
        
        print("AtomDelivery __sending__ end...\n")

    def __receiving__(self):
        import select
        msg = b""
        expected_bytes = self.bufferSize
        while self._receiving:
            #time.sleep(0.001)
            try:  
                if len(list(self.client.values())) == 0:
                    time.sleep(1)
                    continue
                readable, writable, exceptional = select.select(list(self.client.values()),[],[], 1)
                for conn in readable:
                    destaddr = list(self.client.keys())[list(self.client.values()).index(conn)]
                    #print("[DEBUG] {}\n".format(destaddr))
                    if conn in self.cache.keys():
                        msg = self.cache[conn]
                        msg += self._readbytes(conn, expected_bytes - len(msg))
                    else:
                        msg = self._readbytes(conn, expected_bytes)
                    if msg == None:
                        continue
                    
                    if len(msg) == expected_bytes:
                        self.cache.pop(conn, None)
                    else:
                        if len(msg) == 0:
                            continue
                        self.cache[conn] = msg
                        print("[Err]: {}, received {}, should be {}\n".format(destaddr, len(msg), expected_bytes))
                        continue
                    
                    state = (uavPack).from_buffer_copy(msg)
                    #print("[R]< " + repr(state))
                    
                    if (state.zigbee_header.id == 0xdd):
                        group = state.zigbee_header.group
                        id    = state.zigbee_header.address
                        from fwfii.fc import HeartBeat
                        uavid = (group * 1000 + id)

                        if uavid in HeartBeat.flights.keys():
                            if (state.reg == 22):
                                z = state.payload[0] + (state.payload[1] << 8) + (state.payload[2] << 16)
                                if z & 0x800000:
                                    z = -(-0x1000000 + z)
                                else:
                                    z = -z
                                x = ctypes.c_int32(state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)).value
                                y = ctypes.c_int32(state.payload[7] + (state.payload[8] << 8) + (state.payload[9] << 16) + (state.payload[10] << 24)).value
                                yaw = state.payload[11] + (state.payload[12] << 8)
                                HeartBeat.flights[uavid].position = (x, y, z, yaw)
                            elif (state.reg == 4):
                                #print("[R]< " + repr(state))
                                HeartBeat.flights[uavid].obtainStatus(state.payload)
                            elif (state.reg == 100):
                                lat = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                                lng = state.payload[7] + (state.payload[8] << 8) + (state.payload[9] << 16) + (state.payload[10] << 24)
                                #HeartBeat.flights[uavid].setMapOrigin(lat, lng)
                                HeartBeat.flights[uavid].maporigin = (lat, lng)
                            elif (state.reg == 101):
                                utc = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                                HeartBeat.flights[uavid].setUTC(utc)
                            elif (state.reg == 102):
                                lat = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                                lng = state.payload[7] + (state.payload[8] << 8) + (state.payload[9] << 16) + (state.payload[10] << 24)
                                alt = state.payload[11] + (state.payload[12] << 8) + (state.payload[13] << 16)
                                #HeartBeat.flights[uavid].setBase(lat, lng, alt)
                                HeartBeat.flights[uavid].rtkbaseloc = (lat, lng, alt)
                            elif (state.reg == 8):
                                voltage = state.payload[3] + (state.payload[4] << 8) + (state.payload[5] << 16) + (state.payload[6] << 24)
                                HeartBeat.flights[uavid].voltage = voltage
                            if self.vo and self.vo.avalible():
                                self.vo.send((state))
                            msg = b""
                            expected_bytes = self.bufferSize
                    else:
                        self._closeConnection(destaddr)
                        print("[Err]: close {} due to a error package received")
            except Exception:
                if self.vo and self.vo.avalible():
                    traceback.print_exc()
                else:
                    traceback.print_exc()

        print("AtomDelivery __receiving__ end...\n")                
    
    def _closeConnection(self, destaddr):
        if self.client[destaddr] in self.cache.keys():
            self.cache.pop(self.client[destaddr], None)
        self.client[destaddr].close()
        self.client.pop(destaddr, None)
        self.server.pop(destaddr, None)
        self.disconnectnotification(destaddr)

    def writebytes(self, destaddr, packet):
        try:
            if(self.server[destaddr][0]):
                self.client[destaddr].sendall(packet)
                #print("[S]> " + repr(packet))
        except:
            self._closeConnection(destaddr)
            traceback.print_exc()

    def _readbytes(self, conn, count):
        try:
            data = conn.recv(count)
            return data
        except:
            return None
            traceback.print_exc()

    def close(self):
        try:
            self._sending = False
            self._receiving = False
            self._connecting = False

            # 强制关闭所有 socket，让线程从 recv/accept 中退出
            for client in list(self.client.values()):
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                except:
                    pass

            self.s.join(timeout=2)
            self.r.join(timeout=2)
            for thread in list(self.connect_threads.values()):
                thread.join(timeout=2)
        except Exception:
            traceback.print_exc()

class UdpDelivery(AtomDelivery):
    """ Send commands which support for every copter """
    
    def __init__(self, vo):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)
        sock.bind(("0.0.0.0", 10011))
        self._handle_ = sock
        self._sending = True
        self._receiving = True
        self._pause_sending = False
        self.vo = vo
        self.atom = None
        self.INTERVAL = 0.2
        self.s = Thread(target = self.__sending__, args=(), daemon=True)
        self.r = Thread(target = self.__receiving__, args=(), daemon=True)
        self.s.start()
        self.r.start()

    def __sending__(self):
        while self._sending:
            time.sleep(0.001)
            try:
                if self._pause_sending:
                    time.sleep(0.05)
                    continue
                
                try:
                    zigbeepack = AtomRepo.getNext(timeout=0.05)
                except AtomRepo.Empty:
                    continue
                self.atom = zigbeepack
                self.destaddr = ('192.168.{}.{}'.format(zigbeepack.zigbee_header.group, zigbeepack.zigbee_header.address), 10014)
                #print("[S]> " + repr(self.atom))
                #print "[S]> ", ct
                self.writebytes((self.atom))
            except Exception:
                traceback.print_exc()

        print("AtomDelivery __sending__ end...\n")

    def _readbytes(self, count):
        data = ""
        data, _ = self._handle_.recvfrom(count)
        return data
        
    def writebytes(self, buf):
        return self._handle_.sendto(buf, self.destaddr)
          
'''        
if __name__ == '__main__':
    #d = AtomDelivery("COM11", 115200)
    d = wifiDelivery(None)
    d.close()
'''    
    
