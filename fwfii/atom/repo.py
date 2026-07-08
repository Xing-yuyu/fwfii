#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from itertools import count
from queue import Empty, PriorityQueue
import threading

class AtomRepo:
    _fifo   = PriorityQueue()
    _counter = count()
    _lock   = threading.RLock()

    @staticmethod
    def lock():
        AtomRepo._lock.acquire()

    @staticmethod
    def unlock():
        AtomRepo._lock.release()

    @staticmethod
    def getNext(timeout=None):
        _, _, item = AtomRepo._fifo.get(timeout=timeout)
        return item

    @staticmethod
    def isempty():
        return AtomRepo._fifo.empty()

    @staticmethod
    def length():
        return AtomRepo._fifo.qsize()

    @staticmethod
    def storage(zigbeepack, priority=False):
        priority_value = 0 if priority else 1
        with AtomRepo._lock:
            AtomRepo._fifo.put((priority_value, next(AtomRepo._counter), zigbeepack))

    @staticmethod
    def clear():
        while True:
            try:
                AtomRepo._fifo.get_nowait()
            except Empty:
                break

    Empty = Empty
'''        
if __name__ == '__main__':
    from .gen import zigbeePack, dummyPayload, wifiPack
    p = zigbeePack(1001, wifiPack(1, 10, 1, dummyPayload()))
    AtomRepo.storage(p)

    print(repr(AtomRepo.getNext()))
'''
