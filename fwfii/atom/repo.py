#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from multiprocessing import Queue
import time
import threading

class AtomRepo:
    _fifo   = Queue()
    _lock   = threading.Lock()

    @staticmethod
    def lock():
        AtomRepo._lock.acquire()

    @staticmethod
    def unlock():
        AtomRepo._lock.release()

    @staticmethod
    def getNext(timeout=None):
        #AtomRepo._lock.acquire()
        try:
            item = AtomRepo._fifo.get(timeout=timeout)
        except:
            return None
        #AtomRepo._lock.release()
        return item

    @staticmethod
    def isempty():
        return AtomRepo._fifo.empty()

    @staticmethod
    def length():
        return AtomRepo._fifo.qsize()

    @staticmethod
    def storage(zigbeepack):
        AtomRepo._lock.acquire()
        AtomRepo._fifo.put(zigbeepack)
        AtomRepo._lock.release()
'''        
if __name__ == '__main__':
    from .gen import zigbeePack, dummyPayload, wifiPack
    p = zigbeePack(1001, wifiPack(1, 10, 1, dummyPayload()))
    AtomRepo.storage(p)

    print(repr(AtomRepo.getNext()))
'''
