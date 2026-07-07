#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from fwfii.planning.deliver import scriptsGenerator as sg
from fwfii.utils import Delay
from fwfii.fc import GenLsEnd
import traceback

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(description = 'Goertek Roboticks Formation System')
    parser.add_argument('script', help = 'your own formation script')
    parser.add_argument('path', nargs = '?', default = './', help = 'the path you want to save the files for script mode')
    parser.add_argument('append', nargs = '?', default = False, type = bool, help = 'do you want to append the files in this path')
    args = parser.parse_args()

    #
    # Run the file generator
    #
    s = sg(args.path, args.append)
    s.start()

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

    GenLsEnd()
    Delay(100)
    #
    # do not stop the file generator until all of the user's planning is generated
    #
    s.stop()
    s.join()


if __name__ == '__main__':
    main()