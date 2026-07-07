#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.planning.deliver import scriptsTransferOverUart as stu
from fwfii.planning.deliver import scriptsTransferOverSock as sts
from fwfii.fc.odom import VisualOdom as odom
from fwfii.utils import Delay
import socket

def is_valid_ip(ip):
    """Returns true if the given string is a well-formed IP address.

    Supports IPv4 and IPv6.
    """
    if not ip or '\x00' in ip:
        # getaddrinfo resolves empty strings to localhost, and truncates
        # on zero bytes.
        return False
    try:
        res = socket.getaddrinfo(ip, 0, socket.AF_UNSPEC,
                                 socket.SOCK_STREAM,
                                 0, socket.AI_NUMERICHOST)
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise
    return True

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description = 'Goertek Roboticks Formation System')
    parser.add_argument('dest', help = 'destnation address')
    parser.add_argument('dir', help = 'the directory of the files or specified file')
    parser.add_argument('uavid', nargs = '?', type = int, help = 'the uavid for uart delivery')
    args = parser.parse_args()

    #
    # send information to PC
    #
    o = odom()

    if is_valid_ip(args.dest):
        s = sts(args.dir, args.dest, o)
    else:
        s = stu(args.dir, args.dest, args.uavid, o)
    s.start()
    s.join()
    o.close()

if __name__ == '__main__':
    main()
