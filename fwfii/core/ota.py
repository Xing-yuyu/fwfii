#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.planning.deliver import OTA
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
    parser = ArgumentParser(description = 'Goertek Roboticks Formation System - Zigbee mode')
    parser.add_argument('dest', help = 'destnation address')
    parser.add_argument('path', help = 'the directory of the files or specified file')
    parser.add_argument('hw', nargs = '?', default = 0, type = int, help = '0 for F400 led, 1 for f600 led')
    args = parser.parse_args()

    if is_valid_ip(args.dest):
        t = OTA(args.path, args.dest, args.hw)
        t.start()
        t.join()
    else:
        print("Invalid IP address!!!")
        


if __name__ == '__main__':
    main()
