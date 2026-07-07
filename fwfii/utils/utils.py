#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
import time
# import only system from os 
from os import system, name 

# import sleep to show output for some time period 
from time import sleep 
import sys

def Delay(ms):
    '''
    Delay for the specified time, in milisecond.

    *Parameters*:
    * `ms` - milisecond
    '''
    ct = GetCurMs()
    while GetCurMs() - ct < ms:
        time.sleep(0.001)
        
def GetCurMs():
    if (sys.version_info > (3, 3)):
        return int(round(time.perf_counter() * 1000))
    else:
        return int(round(time.clock() * 1000))
    
def GetCurUs():
    if (sys.version_info > (3, 3)):
        return int(round(time.perf_counter() * 1000000))
    else:
        return int(round(time.clock() * 1000000))
    
def GetCurTime():
        if (sys.version_info > (3, 3)):
            return time.perf_counter()
        else:
            return time.clock()

startT = 0
def TimerStart():
    '''
    The start time, usually put it at the beginning of the python script.
    '''
    startT = GetCurMs()

def WaitUtil_Ms(ms):
    '''
    Wait for the timer to reach the specified ms

    *Paramters*
    * `ms` - milisecond
    '''
    while GetCurMs() - startT < ms:
        time.sleep(0.001)

def WaitUntil_S(s):
    while (GetCurMs() - startT) < (s * 1000):
        time.sleep(0.001)

# define our clear function 
def clear(): 

	# for windows 
    if name == 'nt': 
        _ = system('cls') 

	# for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear')

def GetTimerPassMs():
    return GetCurMs() - startT

def TimerClear():
    clear()
                  
'''
if __name__ == '__main__':
	# must call this at the beginning of music
	TimerStart()

	# wait until 2s
	WaitUtil_Ms(2000)
	# now time elaps 2s

	# wait until 3s
	WaitUntil_S(3)
	# now time elaps 3s

	# delay 2s
	Delay(2000)
	# now time elaps 5s
'''