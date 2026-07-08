#!/usr/bin/env python
from __future__ import division, absolute_import, print_function

import traceback
from pathlib import Path
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SOCK_DGRAM, SO_REUSEADDR
import struct
from threading import Thread
import time
from fwfii.atom import AtomRepo, wifiPack, dummyPayload
from fwfii.utils import Delay
from fwfii.fc import Flight, Transfer, Upgrade_LED, End_Transfer, Upgrade_LED2, Upgrade_FC, Upgrade_RK, End_Transfer2

class fileGen:
    def __init__(self, path, id, append = False):
        self._path = Path(path)
        self._path.mkdir(parents=True, exist_ok=True)
        if append:
            self._file = (self._path / (str(id) + '.ls')).open('ab')
        else:
            self._file = (self._path / (str(id) + '.ls')).open('wb')

    def write(self, wifipack):
        self._file.write((wifipack))

    def close(self):
        self._file.close()


def deleteFiles(path, ids):
    base = Path(path)
    for id in ids:
        filename = base / (str(id) + '.ls')
        try:
            filename.unlink()
        except Exception:
            traceback.print_exc()

class scriptsGenerator(Thread):
    def __init__(self, path, append = False):
        super(scriptsGenerator, self).__init__(daemon=True)   
        self._running = True
        self._end = False
        self._path    = Path(path)
        self._append  = append
        self._filelist = {}

    def filelist(self):
        return self._filelist

    def run(self):
        while self._running:
            try:
                zigbeepack = AtomRepo.getNext(timeout=0.05)
            except AtomRepo.Empty:
                continue
            try:
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

    def stop(self, timeout=5):
        deadline = time.monotonic() + timeout
        while not self._end and time.monotonic() < deadline:
            time.sleep(0.01)
        if not self._end:
            raise TimeoutError("mission generation did not receive GenLsEnd")
        self._running = False

class scriptsTransfer(Thread):
    def __init__(self, path, o = None):
        super(scriptsTransfer, self).__init__(daemon=True)
        self._path = Path(path)
        self._readbytes = 512
        self.flight = None
        self.vo = o

    def _startTrans(self, filename):
        filename = Path(filename)
        size = filename.stat().st_size + 4
        uavid = int(filename.stem)
        atom = Transfer(self.flight, 1, size, uavid)
        #print("\r\n[S]> " + repr(atom))
        self.transfer((atom))
        return size

    def _endTrans(self, checksum):
        if self.vo and self.vo.avalible():
            self.vo.send(End_Transfer(self.flight, checksum))

    def run(self):
        try:
            if self._path.is_dir():
                files = sorted(path for path in self._path.iterdir() if path.is_file())
                for file in files:
                    self._deliver(file)
            else:
                self._deliver(self._path)
        finally:
            close = getattr(self, "close", None)
            if close is not None:
                close()

    def _deliver(self, file):
        checksum = 0
        f = None
        try:
            filelen = self._startTrans(file)
            Delay(200)
            f = Path(file).open('rb')
            print("transfering " + str(file))
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
            self._handle.write(buf)
        except Exception:
            traceback.print_exc()

    def close(self):
        self._handle.close()

class scriptsTransferOverSock(scriptsTransfer):
    def __init__(self, path, serverip, o = None, port = 10034, timeout = 2):
        super(scriptsTransferOverSock, self).__init__(path, o)    
        sock = socket(AF_INET, SOCK_STREAM)  
        sock.settimeout(timeout)
        sock.connect((serverip, port))
        self._sock = sock
        uavid = int(serverip.split('.')[2]) * 1000 + int(serverip.split('.')[3])
        self.flight = Flight(uavid)

    def transfer(self, buf):
        try:
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
