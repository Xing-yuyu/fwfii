#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from collections import namedtuple
from fwfii.atom import wifiPack, dummyPayload, flightPayload, lightPayload, lightGroup, buzzerPayload, zigbeePack, uavPack, otaPayload, rcPayload, dutyABPayload
from fwfii.atom import AtomRepo as repo
from .emergency import Emergency_Client as client

#
# Advanced Kinermatic functions 
#

def transfer_self(flight, payload, emergency):
    if emergency:
        client.send(zigbeePack(flight, payload))
    else:
        repo.storage(zigbeePack(flight, payload))

class Displacement_Abs(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False, passby = False):
        super(Displacement_Abs, self).__init__(ts, 16, 1, flightPayload(passby, x, y, z))
        transfer_self(flight, self, emergency)
        
class Displacement_Delta(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False, passby = False):
        super(Displacement_Delta, self).__init__(ts, 17, 1, flightPayload(passby, x, y, z))
        transfer_self(flight, self, emergency)
        
class Velocity(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(Velocity, self).__init__(ts, 18, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)  
        
class Rotation_Abs(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(Rotation_Abs, self).__init__(ts, 19, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)   
        
class Rotation_Delta(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(Rotation_Delta, self).__init__(ts, 20, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)   
        
class AngularVelocity(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(AngularVelocity, self).__init__(ts, 21, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency) 
        
class Acceleration(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(Acceleration, self).__init__(ts, 27, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)        
        
class AngularAcceleration(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(AngularAcceleration, self).__init__(ts, 28, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)  

class ReachPosition(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, passby = False):
        super(ReachPosition, self).__init__(ts, 31, 1, flightPayload(passby, x, y, z))
        transfer_self(flight, self, False)

class ReachAngle(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0):
        super(ReachAngle, self).__init__(ts, 32, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, False)   

class ReachPositionDelta(wifiPack):
     def __init__(self, flight, x, y, z, ts = 0, passby = False):
        super(ReachPositionDelta, self).__init__(ts, 33, 1, flightPayload(passby, x, y, z))
        transfer_self(flight, self, False)

class ReachAngleDelta(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0):
        super(ReachAngleDelta, self).__init__(ts, 34, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, False)       

#   
# System Functions
#

class remoteController(wifiPack):
    def __init__(self, flight, roll, pitch, thr, yaw, ts = 0, emergency = False):
        super(remoteController, self).__init__(ts, 46, 1, rcPayload(roll, pitch, thr, yaw))
        transfer_self(flight, self, emergency)  

class ArmDisarm(wifiPack):
    def __init__(self, flight, arm, ts = 0, emergency = False):
        super(ArmDisarm, self).__init__(ts, 48, 1, flightPayload(0, arm, 0, 0))
        transfer_self(flight, self, emergency)

class SwitchClamp(wifiPack):
    def __init__(self, flight, on, ts=0, emergency=False):
        super(SwitchClamp, self).__init__(ts, 55, 0, flightPayload(0, on, 0, 0))
        transfer_self(flight, self, emergency)

class SwitchMagnet(wifiPack):
    def __init__(self, flight, on, ts=0, emergency=False):
        super(SwitchMagnet, self).__init__(ts, 55, 0, flightPayload(0, on, 0, 0))
        transfer_self(flight, self, emergency)
        
class Land(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        '''
        Make the flight land

        *Parameters*:

        * `flight` - a `Flight` object
        * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
        * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
        '''
        super(Land, self).__init__(ts, 49, 1, flightPayload(0, 1, 0, 0)) 
        transfer_self(flight, self, emergency) 

class RTL(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RTL, self).__init__(ts, 55, 1, flightPayload(0, 1, 0, 0)) 
        transfer_self(flight, self, emergency)            
        
class Takeoff(wifiPack):
    
    def __init__(self, flight, alt, ts = 0, emergency = False):
        '''
        Takeoff the flight to `alt` specified height in centi-meters

        *Parameters*:

        * `flight` - a `Flight` object
        * `alt` - height in centi-meters
        * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
        * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
        '''
        super(Takeoff, self).__init__(ts, 50, 1, flightPayload(0, 0, 0, alt)) 
        transfer_self(flight, self, emergency) 
        
class Stop(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        '''
        Force the motors stop running.

        *Parameters*:

        * `flight` - a `Flight` object
        * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
        * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
        '''
        super(Stop, self).__init__(ts, 51, 1, flightPayload(0, 1, 0, 0)) 
        transfer_self(flight, self, emergency) 
        
class PowerOff(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(PowerOff, self).__init__(ts, 60, 1, flightPayload(0, 1, 0, 0))
        transfer_self(flight, self, emergency) 
        
class Reset(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(Reset, self).__init__(ts, 61, 1, flightPayload(0, 1, 0, 0))
        transfer_self(flight, self, emergency)      

        
class Position(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(Position, self).__init__(ts, 22, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)            
        
class Attitude(wifiPack):
    def __init__(self, flight, x, y, z, ts = 0, emergency = False):
        super(Attitude, self).__init__(ts, 25, 1, flightPayload(0, x, y, z))
        transfer_self(flight, self, emergency)  

class SetFlightMode(wifiPack):
    def __init__(self, flight, mode, ts = 0, emergency = False):
        super(SetFlightMode, self).__init__(ts, 10, 1, flightPayload(0, mode, 0, 0))
        transfer_self(flight, self, emergency)              
        

#
# Mission
# command, 0 - start, 1 - continue, 2 - end
#
class Mission(wifiPack):
    def __init__(self, flight, command, planid = 0, missionid = 0, ts = 0, emergency = False):
        super(Mission, self).__init__(ts, 52, 1, flightPayload(0, command, missionid, planid))
        transfer_self(flight, self, emergency)  

class SetLaunchTime(wifiPack):
    def __init__(self, flight, hour, min, second, planid = 0, missionid = 0, ts = 0, emergency = False):
        hour = (24 + hour - 8) % 24
        utc = hour * 60 * 60 + min * 60 + second
        super(SetLaunchTime, self).__init__(ts, 101, 1, flightPayload(0, utc, missionid, planid))
        transfer_self(flight, self, emergency)  

class RequestLaunchTime(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestLaunchTime, self).__init__(ts, 101, 0, flightPayload(0, 0, 0, 0))
        transfer_self(flight, self, emergency)  

class DelayLaunch(wifiPack):
    def __init__(self, segment, delta, action = 0, utc = 0, ts = 0, emergency = False):
        '''
        Delay time of `delta` to start mission for the segment specified group

        *Parameters*
        * `segement`, the group of flight, 3rd item in a IP address, for example, `192.168.4.10`, the segment is 4
        * `delta`, the delayed time in second
        * `action, 0 mission start, 1 delay land 2 force disarm`
        * `utc`, unused
        * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
        * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
        '''
        super(DelayLaunch, self).__init__(ts, 121, 1, flightPayload(action, utc, delta, 0))
        flight = namedtuple('flight', ['uavid'])
        transfer_self(flight(segment*1000+255), self, emergency)  

class CancelLaunch(wifiPack):
    def __init__(self, segment, delta, utc = 0, ts = 0, emergency = False):
        
        super(CancelLaunch, self).__init__(ts, 122, 1, flightPayload(0, utc, delta, 0))
        flight = namedtuple('flight', ['uavid'])
        transfer_self(flight(segment*1000+255), self, emergency)      

class ConnectionStatus(uavPack):
    def __init__(self, flight, result):
        super(ConnectionStatus, self).__init__(flight, 123, 0, otaPayload(result))      

class Start(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(Start, self).__init__(ts, 124, 0, flightPayload(0, 0, 0, 0))
        transfer_self(flight, self, emergency)

class End(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(End, self).__init__(ts, 125, 0, flightPayload(0, 0, 0, 0))
        transfer_self(flight, self, emergency)

#
# LIGHT SHOW
#
class SetOrigin(wifiPack):
    def __init__(self, flight, lat, lng, ts = 0, emergency = False):
        super(SetOrigin, self).__init__(ts, 100, 1, flightPayload(0, int(lat * 1e7), int(lng * 1e7), 0))
        transfer_self(flight, self, emergency)  

class RequestOrigin(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestOrigin, self).__init__(ts, 100, 0, flightPayload(0, 0, 0, 0))
        transfer_self(flight, self, emergency)  

class SetPoint(wifiPack):
    def __init__(self, flight, xDes, yDes, set = True, ts = 0, emergency = False):
        super(SetPoint, self).__init__(ts, 103, 1, flightPayload(0, xDes, yDes, int(set)))
        transfer_self(flight, self, emergency) 

class RequestPoint(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestPoint, self).__init__(ts, 103, 0, flightPayload(0, 0, 0, 0))
        transfer_self(flight, self, emergency)  

class SetBase(wifiPack):
    def __init__(self, flight, lat, lng, alt, ts = 0, emergency = False):
        super(SetBase, self).__init__(ts, 102, 1, flightPayload(0, int(lat * 1e7), int(lng * 1e7), int(alt * 1e2)))
        transfer_self(flight, self, emergency)

class RequestBase(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestBase, self).__init__(ts, 102, 0, flightPayload(0, 0, 0, 0))
        transfer_self(flight, self, emergency) 

class RequestGrid(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestGrid, self).__init__(ts, 104, 0, flightPayload(0, 0, 0, 0)) 
        transfer_self(flight, self, emergency) 
#
# comamnd 1 - start, 0 - end
# param, checksum when end transfer, pkt number when starting transfer
#
class Transfer(zigbeePack):
    def __init__(self, flight, command, param, uavid):
        super(Transfer, self).__init__(flight, wifiPack(0, 53, 1, flightPayload(0, command, param, uavid)))        

class RequestTransferResult(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestTransferResult, self).__init__(ts, 54, 0, dummyPayload())
        transfer_self(flight, self, emergency)


      
#
# command 1 - enable, 2 - disable
# 
class HeartBeatEnable(wifiPack):
    def __init__(self, command, ts = 0, emergency = False):
        super(HeartBeatEnable, self).__init__(ts, 150, 1, flightPayload(0, command, 0, 0))
        flight = namedtuple('flight', ['uavid'])
        transfer_self(flight(0), self, emergency)

class GenPosfile(wifiPack):
    '''
    Use this func to send a request to generate a current pos file, which is to feed 
    '''
    def __init__(self, ts = 0, emergency = True):
        super(GenPosfile, self).__init__(ts, 151, 1, flightPayload(0, 1, 0, 0))
        flight = namedtuple('flight', ['uavid'])
        transfer_self(flight(0), self, emergency)

class GenLsEnd(wifiPack):
    '''
    Help to flag when is it available to stop ls file generation
    '''
    def __init__(self, ts = 0, emergency = False):
        super(GenLsEnd, self).__init__(ts, 152, 1, flightPayload(0, 0, 0, 0))
        flight = namedtuple('flight', ['uavid'])
        transfer_self(flight(0), self, emergency)

#
# LED Function
#

class LED(wifiPack):
    def __init__(self, flight, id1, mode1, color1, \
                               id2, mode2, color2, \
                               id3, mode3, color3, \
                               id4, mode4, color4, ts = 0, emergency = False):
        super(LED, self).__init__(ts, 29, 1, lightGroup(lightPayload(id1, mode1, color1), \
                                                        lightPayload(id2, mode2, color2), \
                                                        lightPayload(id3, mode3, color3), \
                                                        lightPayload(id4, mode4, color4)))
        transfer_self(flight, self, emergency)     

class DUTY(wifiPack):
    def __init__(self, flight, A, B, ts = 0, emergency = False):
        super(DUTY, self).__init__(ts, 29, 1, dutyABPayload(A, B))
        transfer_self(flight, self, emergency)

class Upgrade_LED(uavPack):
    def __init__(self, flight, filesize):
        super(Upgrade_LED, self).__init__(flight, 65, 1, otaPayload(filesize))

class Upgrade_LED2(zigbeePack):
    def __init__(self, flight, filesize):
        super(Upgrade_LED2, self).__init__(flight, wifiPack(0, 67, 1, flightPayload(0, 0, filesize, 0)))

class Upgrade_FC(zigbeePack):
    def __init__(self, flight, filesize):
        super(Upgrade_FC, self).__init__(flight, wifiPack(0, 68, 1, flightPayload(0, 0, filesize, 0)))

class Upgrade_RK(zigbeePack):
    def __init__(self, flight, filesize):
        super(Upgrade_RK, self).__init__(flight, wifiPack(0, 69, 1, flightPayload(0, 0, filesize, 0)))        

class End_Transfer(uavPack):
    def __init__(self, flight, checksum):
        super(End_Transfer, self).__init__(flight, 66, 1, otaPayload(checksum))   

class End_Transfer2(zigbeePack):
    def __init__(self, flight, checksum):
        super(End_Transfer2, self).__init__(flight, wifiPack(0, 66, 1, flightPayload(0, checksum, 0, 0)))   


#
# Buzzer Function
#
class Sound(wifiPack):
    def __init__(self, flight, mode, freq, duty, on_off, ts = 0, emergency = False):
        super(Sound, self).__init__(ts, 30, 1, buzzerPayload(mode, freq, duty, on_off))
        transfer_self(flight, self, emergency)
        
#
# Motor Function
#

class MotorSpeed(wifiPack):
    def __init__(self, flight, motor_index, speed, ts = 0, emergency = False):
        super(MotorSpeed, self).__init__(ts, 56, 1, flightPayload(0, motor_index, speed, 0))
        transfer_self(flight, self, emergency)
        
class MotorSound(wifiPack):
     def __init__(self, flight, motor_index, frequency, ts = 0, emergency = False):
        super(MotorSound, self).__init__(ts, 58, 1, flightPayload(0, motor_index, frequency, 0))
        transfer_self(flight, self, emergency)
        
class MotorStatus(wifiPack):
     def __init__(self, flight, motor_index, frequency, ts = 0, emergency = False):
        super(MotorStatus, self).__init__(ts, 57, 0, flightPayload(0, motor_index, 0, 0))
        transfer_self(flight, self, emergency)     
#
# Information
#

class RequestVersion(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestVersion, self).__init__(ts, 6, 0, dummyPayload())
        transfer_self(flight, self, emergency)   
        
class RequestSerialNumber(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestSerialNumber, self).__init__(ts, 1, 0, dummyPayload())
        transfer_self(flight, self, emergency)     

class RequestType(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestType, self).__init__(ts, 2, 0, dummyPayload())
        transfer_self(flight, self, emergency)     

class RequestAddress(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestAddress, self).__init__(ts, 3, 0, dummyPayload())
        transfer_self(flight, self, emergency)                

class RequestBatteryCurrent(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestBatteryCurrent, self).__init__(ts, 8, 0, dummyPayload())
        transfer_self(flight, self, emergency)          

class RequestSensorState(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestSensorState, self).__init__(ts, 9, 0, dummyPayload())
        transfer_self(flight, self, emergency)    

class RequestFlightMode(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestFlightMode, self).__init__(ts, 10, 0, dummyPayload())
        transfer_self(flight, self, emergency) 

class RequestPosition(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(RequestPosition, self).__init__(ts, 22, 0, dummyPayload())   
        transfer_self(flight, self, emergency)    

class HeartBeatData(wifiPack):
    def __init__(self, flight, ts = 0, emergency = False):
        super(HeartBeatData, self).__init__(ts, 4, 1, dummyPayload())
        transfer_self(flight, self, emergency)

'''    
if __name__ == '__main__':
    f = Flight(1001)
    Displacement_Abs(f, 3, 4, 5)
    AngularVelocity(f, 3, 4, 5)
    RequestVersion(f)
    RequestPosition(f)
    print(repr(repo.getNext()))
    print(repr(repo.getNext()))
    print(repr(repo.getNext()))
    print(repr(repo.getNext()))
    #i = Information("@#@$#@%@#%@#%@#%#@%$#@$@#$@#")
'''