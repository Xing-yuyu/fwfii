#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import division, absolute_import, print_function
import threading, sys, os, socket, time, struct, select

class R():
    def __init__(self):
        pass
    @staticmethod
    def exit():
        os.system("kill -9 " + str(os.getpid()))

class MulticastServer(threading.Thread):
    def __init__(self, addr, groupaddr):
        threading.Thread.__init__(self)
        self.addr = addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mreq = struct.pack("=4sl", socket.inet_aton(groupaddr), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.bind(addr)
        self.sock = sock
        self.groupaddr = groupaddr
        self.r = 1

    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                infds, outfds, errfds = select.select([sock,],[],[],5)
                if len(infds) > 0:
                    data, client = sock.recvfrom(packSize)
                    print("MulticastServer recv data: %s, client:", data, client)
                    sock.sendto("MulticastServer" + str(i), client)
                    i += 1
            except:
                break

class MulticastClient(threading.Thread):
    def __init__(self, addr, destaddr):
        threading.Thread.__init__(self)
        self.addr = addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        self.sock = sock
        self.destaddr = destaddr
        self.r = 1

    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                sock.sendto("MulticastClient" + str(i), self.destaddr)
                i += 1
                infds, outfds, errfds = select.select([sock,],[],[],5)
                if len(infds) > 0:
                    data, client = sock.recvfrom(packSize)
                    print("MulticastClient recv data: %s, client: %s", data, client)
                time.sleep(0.5)
            except:
                break

class BroadcastServer(threading.Thread):
    def __init__(self, addr):
        threading.Thread.__init__(self)
        self.addr = addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        self.sock = sock
        self.r = 1

    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                infds, outfds, errfds = select.select([sock,],[],[],5)
                if len(infds) > 0:
                    data, client = sock.recvfrom(packSize)
                    print("BroadcastServer recv data: %s, client: %s", data,client)
                    sock.sendto("BroadcastServer" + str(i), client)
                    i += 1
            except:
                break

class BroadcastClient(threading.Thread):
    def __init__(self, addr, destaddr):
        threading.Thread.__init__(self)
        self.addr = addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        self.sock = sock
        self.destaddr = destaddr
        self.r = 1
        
    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                sock.sendto("BroadcastClient" + str(i), self.destaddr)
                i += 1
                infds, outfds, errfds = select.select([sock,],[],[],5)
                if len(infds) > 0:
                    data, client = sock.recvfrom(packSize)
                    print("BroadcastClient recv data: %s, client: %s", data, client)
                time.sleep(0.5)
            except:
                break

class UnicastServer(threading.Thread):
    def __init__(self, addr):
        threading.Thread.__init__(self)
        self.addr = addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        self.sock = sock
        self.r = 1
    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                infds, outfds, errfds = select.select([sock,],[],[],5)
                if len(infds) > 0:
                    data, client = sock.recvfrom(packSize)
                    print("UnicastServer recv data: %s, client: %s", data, client)
                    sock.sendto("UnicastServer" + str(i), client)
                    i += 1
            except:
                break

class UnicastClient(threading.Thread):
    def __init__(self, addr, destaddr):
        threading.Thread.__init__(self)
        self.addr = addr
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        self.sock = sock
        self.destaddr = destaddr
        self.r = 1

    def send(self, msg):
        self.sock.sendto(msg, self.destaddr)

    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                #sock.sendto("UnicastClient" + str(i), self.destaddr)
                i += 1
                infds, outfds, errfds = select.select([sock,],[],[],5)
                if len(infds) > 0:
                    data, client = sock.recvfrom(packSize)
                    print("UnicastClient recv data: %s, client: %s", data, client)
                time.sleep(0.5)
            except:
                break

class StreamServer(threading.Thread):
    def __init__(self, addr):
        threading.Thread.__init__(self)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(addr)
        sock.listen(1)
        self.sock = sock
        self.r = 1

    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        conn, client_addr = sock.accept()
        while(self.r):
            print(client_addr)
            try:
                #infds, outfds, errfds = select.select([conn,],[],[],5)
                #if len(infds) > 0:
                data = conn.recv(packSize)
                print("StreamServer recv data: %s", data)
                conn.sendall("StreamServer" + str(i))
                i += 1
            except:
                break

class StreamClient(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        sock.connect(server)
        self.sock = sock
        self.r = 1

    def run(self):
        sock = self.sock
        packSize = 1024
        i = 0
        while(self.r):
            try:
                sock.sendall("StreamClient" + str(i))
                i += 1
                #infds, outfds, errfds = select.select([sock,],[],[],5)
                #if len(infds) > 0:
                data = sock.recv(packSize)
                print("StreamClient recv data: %s", data)
                time.sleep(0.5)
            except:
                break

def main(argv):
    try:
        bserver = BroadcastServer(("0.0.0.0", 2101))
        bserver.start()
        '''
        mserver = MulticastServer(("0.0.0.0", 10010), "224.0.1.255")
        mserver.start()
        mclient = MulticastClient(("0.0.0.0", 10011), ("224.0.1.255", 10010))
        mclient.start()
        '''

        '''
        bserver = BroadcastServer(("0.0.0.0", 10012))
        bserver.start()
        bclient = BroadcastClient(("0.0.0.0", 10013), ("255.255.255.255", 10012))
        bclient.start()
        
        
        userver = UnicastServer(("0.0.0.0", 10014))
        userver.start()
        #uclient = UnicastClient(("0.0.0.0", 10015), ("127.0.0.1", 10014))
        #uclient.start()
        #uclient2 = UnicastClient(("0.0.0.0", 10017), ("127.0.0.1", 10014))
        #uclient2.start()

 
        sserver = StreamServer(("0.0.0.0", 2101))
        sserver.start()

        sclient = StreamClient(("127.0.0.1", 10018))
        sclient.start()
        '''
    except:
        R.exit()
    while 1:
        try:
            time.sleep(1000)
        except:
            R.exit()


if __name__ == "__main__":
    main(sys.argv)
  