#!/usr/bin/env python
from __future__ import division, absolute_import, print_function

import os
import traceback
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SOCK_DGRAM, SO_REUSEADDR
import struct
from threading import Thread
from fwfii.atom import AtomRepo, wifiPack, dummyPayload
from fwfii.utils import Delay
from fwfii.fc import Flight, Transfer, Upgrade_LED, End_Transfer, Upgrade_LED2, Upgrade_FC, Upgrade_RK, End_Transfer2

class fileGen:
    def __init__(self, path, id, append = False):
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except Exception:
                traceback.print_exc()
        if append:
            self._file = open(path + '/' + str(id) + '.ls', 'ab')
        else:
            self._file = open(path + '/' + str(id) + '.ls', 'wb')

    def write(self, wifipack):
        if not isinstance(wifipack, (bytes, bytearray, memoryview)):
            wifipack = bytes(wifipack)
        self._file.write(wifipack)

    def close(self):
        self._file.close()


def deleteFiles(path, ids):
    for id in ids:
        filename = path + '/' + str(id) + '.ls'
        try:
            os.remove(filename)
        except Exception:
            traceback.print_exc()

class scriptsGenerator(Thread):
    def __init__(self, path, append = False):
        super(scriptsGenerator, self).__init__()   
        self._running = True
        self._end = False
        self._path    = path
        self._append  = append
        self._filelist = {}

    def filelist(self):
        return self._filelist

    def run(self):
        while self._running:
            while not AtomRepo.isempty():
                try:
                    zigbeepack = AtomRepo.getNext()
                    element = (wifiPack).from_buffer_copy(zigbeepack.payload)
                    if element.pack_header.reg == 152:
                        self._end = True
                        break
                    uavid = zigbeepack.zigbee_header.address + zigbeepack.zigbee_header.group * 1000
                    if str(uavid) not in self._filelist.keys():
                        self._filelist[str(uavid)] = fileGen(self._path, uavid, self._append)
                        dummy = wifiPack(0, 0, 0, dummyPayload())
                        self._filelist[str(uavid)].write(dummy)
                    
                    self._filelist[str(uavid)].write(element)
                except Exception:
                    traceback.print_exc()

        for f in self._filelist.values():
            try:
                f.close()
            except Exception:
                traceback.print_exc()

    def stop(self):
        while not self._end:
            pass
        self._running = False

class scriptsTransfer(Thread):
    def __init__(self, path, o = None):
        super(scriptsTransfer, self).__init__()
        self._path = path
        self._readbytes = 512
        self.flight = None
        self.vo = o

    def _startTrans(self, filename):
        size = os.path.getsize(filename) + 4
        uavid = int(filename.split('\\')[-1].split('.')[0])
        atom = Transfer(self.flight, 1, size, uavid)
        #print("\r\n[S]> " + repr(atom))
        self.transfer((atom))
        return size

    def _endTrans(self, checksum):
        if self.vo and self.vo.avalible():
            self.vo.send(End_Transfer(self.flight, checksum))

    def run(self):
        if os.path.isdir(self._path):
            files = os.listdir(self._path)
            for file in files:
                if not os.path.isdir(file):
                    self._deliver(self._path + "\\" + file)
        else:
            self._deliver(self._path)

    def _deliver(self, file):
        checksum = 0
        f = None
        try:
            filelen = self._startTrans(file)
            Delay(200)
            f = open(file, 'rb')
            print("transfering " + file)
            sentbytes = 0
            while True:
                bytes = f.read(self._readbytes)
                if 0 == len(bytes):
                    break
                sentbytes += len(bytes)
                #print("%f%\r\n" % (sentbytes * 1.0 / filelen) * 100)
                print("%d/%d" % (sentbytes, filelen))
                for byte in bytearray(bytes):
                    checksum += byte
                self.transfer(bytes)
                self.wait()

            f.close()
            self.transfer(struct.pack("<I", checksum & 0xFFFFFFFF))    
            self._endTrans(checksum & 0xFFFFFFFF)
            print("Done!!! checksum 0x%08x\r\n" % (checksum & 0xFFFFFFFF))
        except Exception:
            traceback.print_exc()

    def wait(self):
        pass

    def transfer(self, buf):
        pass

class scriptsTransferOverUart(scriptsTransfer):
    def __init__(self, path, port, uavid, o = None):
        super(scriptsTransferOverUart, self).__init__(path, o)
        import serial
        self._handle = serial.Serial(port, 115200, timeout = 2)        
        self.flight = Flight(uavid)

    def transfer(self, buf):
        try:
            if not isinstance(buf, (bytes, bytearray, memoryview)):
                buf = bytes(buf)
            self._handle.write(buf)
        except Exception:
            traceback.print_exc()

    def close(self):
        self._handle.close()

class scriptsTransferOverSock(scriptsTransfer):
    def __init__(self, path, serverip, o = None):
        super(scriptsTransferOverSock, self).__init__(path, o)    
        sock = socket(AF_INET, SOCK_STREAM)  
        #sock.settimeout(1)
        sock.connect((serverip, 10034))
        self._sock = sock
        uavid = int(serverip.split('.')[2]) * 1000 + int(serverip.split('.')[3])
        self.flight = Flight(uavid)

    def transfer(self, buf):
        try:
            if not isinstance(buf, (bytes, bytearray, memoryview)):
                buf = bytes(buf)
            self._sock.sendall(buf)
        except Exception:
            traceback.print_exc()

    def wait(self):
        Delay(40)

    def close(self):
        self._sock.close()

class OTA(scriptsTransferOverSock):
    def __init__(self, path, serverip, hw):
        super(OTA, self).__init__(path, serverip)
        self.hw = hw

    def _startTrans(self, filename):
        size = os.path.getsize(filename) + 4
        if self.hw == 0:
            self.transfer((Upgrade_LED(self.flight, size)))
        elif self.hw == 1:
            self.transfer((Upgrade_LED2(self.flight, size)))
        elif self.hw == 2:
            self.transfer((Upgrade_FC(self.flight, size)))
        elif self.hw == 3:
            self.transfer((Upgrade_RK(self.flight, size)))
        return size

    def _endTrans(self, checksum):
        if self.vo and self.vo.avalible():
            self.vo.send(End_Transfer(self.flight, checksum))


    def wait(self):
        Delay(10)
'''
if __name__ == '__main__':
    scriptsTransferOverUart('./cache', 'com18').start()
'''    