#!/usr/bin/env python
from __future__ import division, absolute_import, print_function

import math
import os

from .advanced import *
from fwfii.utils import Delay, GetCurMs
from math import sqrt, sin, cos, pi

Markers = {}


#
# add markers to local marker repo
#
def AddMark(name, x, y, z):
    '''
    Add a marker with (x, y, z) coordinate and name it to `name`

    *Parameters*:

    * `name` - the marker's name, a string
    * `x` - the x coordinate
    * `y` - the y coordinate
    * `z` - the z coordinate
    '''
    Markers[name] = (x, y, z)


def ReadMarker(name):
    if name in Markers.keys():
        return Markers[name]
    else:
        return None


def MaxVelXY(flight, v, ts=0, emergency=False):
    '''
    Set the maximum velocity in x, y axis

    *Parameters*:

    * `flight` - a `Flight` object
    * `v` - the maximum velocity, cm/s, [0 ~ 500]
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if v < 0:
        v = 0
    elif v > 500:
        v = 500
    Velocity(flight, int(v * 100), int(v * 100), -1, ts, emergency)


#
# Set the max velocity for z axis
# flight, the flight instance
# v, the maximum velocity
#
def MaxVelZ(flight, v, ts=0, emergency=False):
    '''
    Set the maximum velocity in z axis

    *Parameters*:

    * `flight` - a `Flight` object
    * `v` - the maximum velocity, cm/s, [0 ~ 300]
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if v < 0:
        v = 0
    elif v > 300:
        v = 300
    Velocity(flight, -1, -1, int(v * 100), ts, emergency)


def MaxAccXY(flight, a, ts=0, emergency=False):
    '''
    Set the maximum acceleration in x, y axis

    *Parameters*:

    * `flight` - a `Flight` object
    * `a` - the maximum accleration, cm/s/s, [0 ~ 500]
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if a < 0:
        a = 0
    elif a > 500:
        a = 500
    Acceleration(flight, int(a * 100), int(a * 100), -1, ts, emergency)


def MaxAccZ(flight, a, ts=0, emergency=False):
    '''
    Set the maximum acceleration in z axis

    *Parameters*:

    * `flight` - a `Flight` object
    * `a` - the maximum accleration, cm/s/s, [0 ~ 500]
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if a < 0:
        a = 0
    elif a > 500:
        a = 500
    Acceleration(flight, -1, -1, int(a * 100), ts, emergency)


def MaxAngularRate(flight, w, ts=0, emergency=False):
    '''
    Set the maximum angular rate

    *Parameters*:

    * `flight` - a `Flight` object
    * `w` - the maximum angular rate, degree/s, [0 ~ 120]
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if w < 0:
        w = 0
    elif w > 120:
        w = 120
    AngularVelocity(flight, -1, -1, int(w * 100), ts, emergency)


def Arm(flight, ts=0, emergency=False):
    '''
    Arm the flight, the blades of the flight start running.

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency arm command if the copters has already been running your scripts if set it as True.
    '''
    ArmDisarm(flight, 1, ts, emergency)


#
# flight, the flight instance
#    
def Disarm(flight, ts=0, emergency=False):
    '''
    Disarm the flight, the blades of the flight stop running.

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    ArmDisarm(flight, 0, ts, emergency)


def Clamp(flight, on, ts=0, emergency=False):
    SwitchClamp(flight, on, ts, emergency)

def Magnet(flight, on, ts=0, emergency=False):
    SwitchMagnet(flight, on, ts, emergency)

#
# flight, the flight instance
#
def ProgrammingMode(flight, ts=0, emergency=False):
    '''
    Set the flight in command mode to support graphic programming.

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    SetFlightMode(flight, 4, ts, emergency)


#
# flight ,the flight instance
#
def PlanningMode(flight, ts=0, emergency=False):
    '''
    Set the flight in script mode to support mission planning.

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    SetFlightMode(flight, 3, ts, emergency)


#
# flight, the flight instance
#
def MissionStart(flight, ts=0, emergency=False):
    '''
    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Mission(flight, 0, ts, emergency)


#
# flight, the flight instance
#
def MissionContinue(flight, ts=0, emergency=False):
    '''
    Continue to run the planning stored in built-in FLASH or SD-card

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Mission(flight, 1, ts, emergency)


#
# flight, the flight instance
#
def MissionPause(flight, ts=0, emergency=False):
    '''
    Pause the mission

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Mission(flight, 2, ts, emergency)


#
# flight, the flight instance
# orientation, 0 for +pitch, 1 for -pitch, 2 for +roll, otherwise for -roll
#
def Flip(flight, axis, ts=0, emergency=False):
    '''
    Flip the flight in the air.

    *Parameters*: 

    * `flight` - a `Flight` object
    * `aixs` - a string, flip according the specified axis, 'x', '-x' is available now, 'y', '-y' is unavailable.
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if 'x' == axis:
        Rotation_Delta(flight, 360, 0, 0, ts, emergency)
    elif '-x' == axis:
        Rotation_Delta(flight, -360, 0, 0, ts, emergency)
    elif 'y' == axis:
        Rotation_Delta(flight, 0, 360, 0, ts, emergency)
    elif '-y' == axis:
        Rotation_Delta(flight, 0, -360, 0, ts, emergency)


def Forward(flight, displacement, ts=0, emergency=False, passby=False):
    '''
    Move forward the flight of `displacement` specified distance in cm.

    *Parameters*:

    * `flight` - a `Flight` object
    * `displacement` - the displacement in centi-meters
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, int(displacement * 100), 0, 0, ts, emergency, passby)


def Backward(flight, displacement, ts=0, emergency=False, passby=False):
    '''
    Move backward the flight of `displacement` specified distance in cm.

    *Parameters*:

    * `flight` - a `Flight` object
    * `displacement` - the displacement in centi-meters
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, int(-displacement * 100), 0, 0, ts, emergency, passby)


def Left(flight, displacement, ts=0, emergency=False, passby=False):
    '''
    Move left the flight of `displacement` specified distance in cm.

    *Parameters*:

    * `flight` - a `Flight` object
    * `displacement` - the displacement in centi-meters
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, 0, int(-displacement * 100), 0, ts, emergency, passby)


def Right(flight, displacement, ts=0, emergency=False, passby=False):
    '''
    Move right the flight of `displacement` specified distance in cm.

    *Parameters*:

    * `flight` - a `Flight` object
    * `displacement` - the displacement in centi-meters
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, 0, int(displacement * 100), 0, ts, emergency, passby)


def Up(flight, displacement, ts=0, emergency=False, passby=False):
    '''
    Move up the flight of `displacement` specified distance in cm.

    *Parameters*:

    * `flight` - a `Flight` object
    * `displacement` - the displacement in centi-meters
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
        '''
    Displacement_Delta(flight, 0, 0, int(displacement * 100), ts, emergency, passby)


def Down(flight, displacement, ts=0, emergency=False, passby=False):
    '''
    Move down the flight of `displacement` specified distance in cm.

    *Parameters*:

    * `flight` - a `Flight` object
    * `displacement` - the displacement in centi-meters
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, 0, 0, int(-displacement * 100), ts, emergency, passby)


def Move2(flight, x, y, z, ts=0, emergency=False, passby=False):
    '''
    Move the flight to the specified coordinate

    *Parameters*:

    * `flight` - a `Flight` object
    * `x` - the x coordinate, in cm
    * `y` - the y coordinate, in cm
    * `z` - the z coordinate, in cm
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Abs(flight, int(y * 100), int(x * 100), int(z * 100), ts, emergency, passby)


def Move2Marker(flight, marker, ts=0, emergency=False, passby=False):
    '''
    Move the flight to marker specified cooridnate, you MUST have already added this marker by
    `AddMarker`.

    *Parameters*:

    * `flight` - a `Flight` object
    * `marker` - the name of the marker, a string
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if marker not in Markers.keys():
        print("CANNOT find such %s in markers" % marker)
        return
    Move2(flight, Markers[marker][0], Markers[marker][1], Markers[marker][2], ts, emergency, passby)


def MoveDelta(flight, dx, dy, dz, ts=0, emergency=False, passby=False):
    '''
    Make the flight move a displacment from its current location.

    *Parameters*:

    * `flight` - a `Flight` object
    * `dx` - the displacement in x axis, in cm
    * `dy` - the displacement in y axis, in cm
    * `dz` - the displacement in z axis, in cm
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, int(dy * 100), int(dx * 100), int(dz * 100), ts, emergency, passby)


def ReadPosition(flight):
    from .heartbeat import HeartBeat
    for uavid, f in HeartBeat.flights.items():
        print(flight.uavid, uavid)
        if uavid == flight.uavid:
            print(f.fcstatus)
            return f.position
    return None


def ReadPosition2(flight):
    appData = os.getenv("APPDATA")
    if not os.path.exists(appData + '/FlightPos/' + str(flight.uavid)):
        return None
    pos = None
    try:
        fp = open(appData + '/FlightPos/' + str(flight.uavid), 'r')
        line = fp.readline()
        line = line.strip('(').strip(')').split(',')
        pos = [int(line[1]), int(line[0]), int(line[2])]
        fp.close()
    except:
        pass
    return pos


def ReadX(flight):
    pos = ReadPosition2(flight)
    if pos == None:
        return None
    else:
        return pos[0]


def ReadY(flight):
    pos = ReadPosition2(flight)
    if pos == None:
        return None
    else:
        return pos[1]


def ReadZ(flight):
    pos = ReadPosition2(flight)
    if pos == None:
        return None
    else:
        return pos[2]


def Arrived(flight, x, y, z):
    pos = ReadPosition2(flight)
    if pos == None:
        return False

    # cur_x, cur_y, cur_z, _ = pos
    cur_x = pos[0]
    cur_y = pos[1]
    cur_z = pos[2]
    radius = 15
    # if ((cur_x - x) ** (cur_x - x) + (cur_y - y) ** (cur_y - y) + (cur_z - z) ** (cur_z - z)) < (radius ** radius) and \
    #         abs(cur_z - z) < 0.5 * radius:
    #     return True
    # else:
    #     return False
    ret = (cur_x - x) * (cur_x - x) + (cur_y - y) * (cur_y - y) < radius * radius
    return ret


def ArrivedMarker(flight, marker):
    if marker not in Markers.keys():
        print("CANNOT find such %s in markers" % marker)
        return False
    return Arrived(flight, Markers[marker][0], Markers[marker][1], Markers[marker][2])


#
# timeout: ms
#
def WaitUntilReach(flight, x, y, z, timeout=0):
    start = GetCurMs()
    while True:
        if (timeout > 0) and (GetCurMs() - start > timeout):
            return False
        if Arrived(flight, x, y, z):
            return True
        Delay(200)


def Reach(flight, x, y, z, ts=0, online=False, timeout=0, passby=False):
    ReachPosition(flight, int(y * 100), int(x * 100), int(z * 100), ts, passby)
    if online == False:
        return True
    else:
        return WaitUntilReach(flight, x, y, z, timeout)


def ReachDelta(flight, dx, dy, dz, ts=0, online=False, timeout=0, passby=False):
    ReachPositionDelta(flight, int(dy * 100), int(dx * 100), int(dz * 100), ts, passby)
    if online == False:
        return True
    else:
        cur_pos = ReadPosition(flight)
        if cur_pos == None:
            return False

        return WaitUntilReach(flight, cur_pos[0] + dx, cur_pos[1] + dy, cur_pos[2] + dz, timeout)


def ReachMarker(flight, marker, ts=0, online=False, timeout=0, passby=False):
    if marker not in Markers.keys():
        print("CANNOT find the %s in markers" % marker)
        return
    return Reach(flight, Markers[marker][0], Markers[marker][1], Markers[marker][2], ts, online, timeout, passby)


def Nod(flight, axis, d, ts=0, emergency=False):
    '''
    Make the flight do a nod like action along with the specified axis.

    *Parameters*:

    * `flight` - a `Flight` object
    * `axis` - the specified axis, `x`, `-x`, `y`, `-y`, a string
    * `d` - the distance that you want the flight to move, cm, [0 ~ 30]
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if d < 0:
        d = 0
    elif d > 30:
        d = 30

    MaxAccXY(flight, 500, ts, emergency)

    if axis == 'y':
        Forward(flight, d, ts + 100, emergency)
    elif axis == '-y':
        Backward(flight, d, ts + 100, emergency)
    elif axis == 'x':
        Right(flight, d, ts + 100, emergency)
    elif axis == '-x':
        Left(flight, d, ts + 100, emergency)

    if ts == 0:
        Delay(100)
    MaxAccXY(flight, 200, ts + 100, emergency)


def RoundInAir(flight, x, y, cx, cy, h, direction, speed, ts=0):
    MaxAccXY(flight, 200, ts, False)
    Move2(flight, x, y, h, ts)
    radius = math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy))
    if radius < 40:
        return
    tmpX = x - cx
    tmpY = y - cy
    startAngle = math.asin(tmpY / radius) * 180 / math.pi
    if (tmpX >= 0 and tmpY >= 0):
        pass
    elif (tmpX < 0 and tmpY >= 0):
        startAngle = 180 - startAngle
    elif (tmpX < 0 and tmpY < 0):
        startAngle += 270
    elif (tmpX >= 0 and tmpY < 0):
        startAngle += 360

    tmpTs = ts + 3000
    lastX = x
    lastY = y
    delta = (speed - 80) * 4.8
    MaxAccXY(flight, speed, tmpTs, False)
    for i in range(12):
        if direction == 1:
            startAngle += 30
        else:
            startAngle -= 30
        if startAngle < 0:
            startAngle += 360
        if startAngle > 360:
            startAngle -= 360
        tarX = int(math.cos(startAngle * (math.pi / 180)) * radius) + cx
        tarY = int(math.sin(startAngle * (math.pi / 180)) * radius) + cy
        distance = math.sqrt((tarX - lastX) * (tarX - lastX) + (tarY - lastY) * (tarY - lastY))
        tt = distance / speed * 1000 + delta
        tmpTs = int(tmpTs + tt)
        lastX = tarX
        lastY = tarY
        Move2(flight, int(tarX), int(tarY), h, tmpTs)


def SimpleHarmonic2(flight, axis, amp=50, omega=90, phase=0, loop=1, ts=0):
    MaxAccZ(flight, 200, ts, False)
    if axis == 'z':
        Up(flight, amp, ts + 100)
        Down(flight, int(amp * 2), ts + 1000)
        Up(flight, amp, ts + 3000)
    elif axis == '-z':
        Down(flight, amp, ts + 100)
        Up(flight, int(amp * 2), ts + 1000)
        Down(flight, amp, ts + 3000)
    elif axis == 'y':
        Forward(flight, amp, ts + 100)
        Backward(flight, int(amp * 2), ts + 1000)
        Forward(flight, amp, ts + 3000)
    elif axis == '-y':
        Backward(flight, amp, ts + 100)
        Forward(flight, int(amp * 2), ts + 1000)
        Backward(flight, amp, ts + 3000)
    elif axis == 'x':
        Left(flight, amp, ts + 100)
        Right(flight, int(amp * 2), ts + 1000)
        Left(flight, amp, ts + 3000)
    elif axis == '-x':
        Right(flight, amp, ts + 100)
        Left(flight, int(amp * 2), ts + 1000)
        Right(flight, amp, ts + 3000)


# def SimpleHarmonic2(flight, axis, amp = 50, omega = 90, phase = 0, loop = 1, ts = 0):
#    cur_pos = ReadPosition(flight)
#    return SimpleHarmonic(flight, axis, cur_pos[0], cur_pos[1], cur_pos[2], amp, omega, phase, loop, ts)

#
# omega, 90, 180, 360
#
def SimpleHarmonic(flight, axis, x, y, z, amp=50, omega=90, phase=0, loop=1, ts=0, emergency=False):
    '''
    Make the flight do a simple harmonic movement along with the specified axis.    

    $$
    y = A*sin(\omega*t+\phi)
    $$

    *Parameters*:

    * `flight` - a `Flight` object
    * `axis` -  a string, the specified axis, `x`, `-x`, `y`, `-y`, `z`, `-z`
    * `x` - the x coordinate of the location you want to do the action
    * `y` - the y coordinate of the location you want to do the action
    * `z` - the z coordinate of the location you want to do the action
    * `amp` - the amplitude of the simple harmonic
    * `omega` - the angular frequency of the harmonic, 90, 120, 180, 360
    * `phase` - the phase of the simple harmonic
    * `loop` - how many period you want to move
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    freq = (omega / 360)
    T = loop / freq
    t = 0

    MaxAccXY(flight, 500, ts, emergency)
    MaxAccZ(flight, 500, ts, emergency)

    while t < T:
        if axis == 'x':
            x_ = amp * sin(2 * pi * freq * t + phase) + x
            Move2(flight, int(x_), y, z, int(ts + t * 1000 + 100), emergency)
        elif axis == '-x':
            x_ = -amp * sin(2 * pi * freq * t + phase) + x
            Move2(flight, int(x_), y, z, int(ts + t * 1000 + 100), emergency)
        elif axis == 'y':
            y_ = amp * sin(2 * pi * freq * t + phase) + y
            Move2(flight, x, int(y_), z, int(ts + t * 1000 + 100), emergency)
        elif axis == '-x':
            y_ = -amp * sin(2 * pi * freq * t + phase) + y
            Move2(flight, x, int(y_), z, int(ts + t * 1000 + 100), emergency)
        elif axis == 'z':
            z_ = amp * sin(2 * pi * freq * t + phase) + z
            Move2(flight, x, y, int(z_), int(ts + t * 1000 + 100), emergency)
        elif axis == '-z':
            z_ = -amp * sin(2 * pi * freq * t + phase) + z
            Move2(flight, x, y, int(z_), int(ts + t * 1000 + 100), emergency)
        t += 0.1
        if ts == 0:
            Delay(10)

    MaxAccXY(flight, 200, int(ts + t * 1000 + 100), emergency)
    MaxAccZ(flight, 200, int(ts + t * 1000 + 100), emergency)


def CylindricalSpiral(flight, axis, marker, clockwise=True, omega=90, radius=50, distance=100, loop=1, ts=0,
                      emergency=False):
    '''
    Make the flight do a cylindrical spiral movement along with the specified axis.

    $$
    x = r * cos(w*t)
    y = r * sin(w*t)
    z = d * w / (2 * pi) * t
    $$

    *Parameters*:

    * `flight` - a `Flight` object
    * `axis` - , a string, the specified axis, `x`, `-x`, `y`, `-y`, `z`, `-z`
    * `marker` - the specified marker
    * `clockwise` - True or False
    * `omega` - the angular frequency of the harmonic, 90, 120, 180, 360
    * `radius` - the radius of the CylindricalSpiral
    * `distance` - the distance moved
    * `loop` - the period, default is 1
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    t = 0
    MaxAccXY(flight, 500, ts, emergency)
    freq = (omega / 360)
    if marker not in Markers.keys():
        print("CANNOT find such %s in markers" % marker)
        return
    x, y, z = Markers[marker]
    if clockwise:
        direction = 1
    else:
        direction = -1
    next_x = x
    next_y = y
    next_z = z
    if axis == 'x':
        while next_x < (x + distance):
            next_z = radius * cos(2 * pi * freq * t * direction) + z
            next_y = radius * sin(2 * pi * freq * t * direction) + y
            next_x = distance / loop * freq * t + x
            Move2(flight, int(next_x), int(next_y), int(next_z), int(ts + t * 1000 + 100), emergency)
            t += 0.01
            if ts == 0:
                Delay(10)
    elif axis == '-x':
        while next_x > (x - distance):
            next_z = radius * cos(2 * pi * freq * t * direction) + z
            next_y = radius * sin(2 * pi * freq * t * direction) + y
            next_x = -distance / loop * freq * t + x
            Move2(flight, int(next_x), int(next_y), int(next_z), int(ts + t * 1000 + 100), emergency)
            t += 0.01
            if ts == 0:
                Delay(10)
    elif axis == 'y':
        while next_y < (y + distance):
            next_z = radius * cos(2 * pi * freq * t * direction) + z
            next_x = radius * sin(2 * pi * freq * t * direction) + x
            next_y = distance / loop * freq * t + y
            Move2(flight, int(next_x), int(next_y), int(next_z), int(ts + t * 1000 + 100), emergency)
            t += 0.01
            if ts == 0:
                Delay(10)
    elif axis == '-y':
        while next_y > (y - distance):
            next_z = radius * cos(2 * pi * freq * t * direction) + z
            next_x = radius * sin(2 * pi * freq * t * direction) + x
            next_y = -distance / loop * freq * t + y
            Move2(flight, int(next_x), int(next_y), int(next_z), int(ts + t * 1000 + 100), emergency)
            t += 0.01
            if ts == 0:
                Delay(10)
    elif axis == 'z':
        MaxAccZ(flight, 500, ts, emergency)
        while next_z < (z + distance):
            next_x = radius * cos(2 * pi * freq * t * direction) + x
            next_y = radius * sin(2 * pi * freq * t * direction) + y
            next_z = distance / loop * freq * t + z
            Move2(flight, int(next_x), int(next_y), int(next_z), int(ts + t * 1000 + 100), emergency)
            t += 0.01
            if ts == 0:
                Delay(10)
    elif axis == '-z':
        MaxAccZ(flight, 500, ts, emergency)
        while next_z > (z - distance):
            next_x = radius * cos(2 * pi * freq * t * direction) + x
            next_y = radius * sin(2 * pi * freq * t * direction) + y
            next_z = -distance / loop * freq * t + z
            Move2(flight, int(next_x), int(next_y), int(next_z), int(ts + t * 1000 + 100), emergency)
            t += 0.01
            if ts == 0:
                Delay(10)
        MaxAccZ(flight, 500, int(ts + t * 1000 + 100), emergency)


def MovewHeading(flight, axis, d, clockwise, angle, ts=0, emergency=False):
    '''
    Move a `d` displacement along with the specified axis.

    *Parameters*:
    * `flight` - a `Flight` object
    * `axis` - the specified axis, `x`, `-x`, `y`, `-y`a string
    * `d` - the displacement
    * `clockwise` - True or False
    * `angle` - the heading angle
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if angle < 0:
        angle = 0
    elif angle > 720:
        angle = 720

    if axis == 'y':
        Forward(flight, d, ts, emergency)
    elif axis == '-y':
        Backward(flight, d, ts, emergency)
    elif axis == 'x':
        Right(flight, d, ts, emergency)
    elif axis == '-x':
        Left(flight, d, ts, emergency)
    elif axis == 'z':
        Up(flight, d, ts, emergency)
    elif axis == '-z':
        Down(flight, d, ts, emergency)

    MaxAngularRate(flight, 120, ts + 3, emergency)
    MaxAccXY(flight, 500, ts + 6, emergency)
    T = 0
    if ((axis == 'z') or (axis == '-z')):
        velZ = d / (angle / 120)
        MaxVelZ(flight, velZ, ts + 9, emergency)
        if velZ > 300:
            T = (d / 300) * 1000
            MaxAngularRate(flight, angle / T, ts + 12, emergency)
        else:
            T = (angle / 120) * 1000
    else:
        velXY = d / (angle / 120)
        MaxVelXY(flight, velXY, ts + 9, emergency)
        if velXY > 500:
            T = (d / 500) * 1000
            MaxAngularRate(flight, angle / T, ts + 12, emergency)
        else:
            T = (angle / 120) * 1000

    t = 0
    while t < T:
        da = angle / (T / 200)
        # print(da)
        t += 200
        if clockwise:
            Rotation_Delta(flight, 'r', int(da), int(ts + t), emergency)
        else:
            Rotation_Delta(flight, 'l', int(da), int(ts + t), emergency)
        if ts == 0:
            Delay(200)


'''
#
# flight, the flight instance
# angle, unit, centi-degree
# 
def Roll(flight, angle, ts = 0, emergency = False):
    Rotation_Abs(flight, 0, angle, 0, ts, emergency)

#
# flight, the flight instance
# angle, unit, centi-degree
# 
def Pitch(flight, angle, ts = 0, emergency = False):
    Rotation_Abs(flight, 0, angle, 0, ts, emergency)

#
# flight, the flight instance
# angle, unit, centi-degree
#    
def Roll_Origin(flight, angle, time, ts = 0, emergency = False):
    Rotation_Abs(flight, angle, 0, 0, ts, emergency)
    Delay(time)
    Displacement_Delta(flight, 0, 0, 0, ts, emergency)

#
# flight, the flight instance
# angle, unit, centi-degree
#  
def Pitch_Origin(flight, angle, time, ts = 0, emergency = False):
    Rotation_Abs(flight, 0, angle, 0, ts, emergency)
    Delay(time)
    Displacement_Delta(flight, 0, 0, 0, ts, emergency)
'''


#
# flight, the flight instance
# angle, unit, centi-degree
#
def Yaw(flight, direction, angle, ts=0, emergency=False):
    '''
    Rotate the flight's heading a `angle` specified angle according to the `direction`

    *Parameters*:

    * `flight` - a `Flight` object
    * `direction`, a string, 'l' represents ccw and 'r' represents cw. 
    * `angel` - the angle in centi-degree
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if angle == 360:
        angle = 359
    if angle == -360:
        angle = -359
    if direction == 'l':
        Rotation_Delta(flight, 0, 0, int(angle * 100), ts, emergency)
    elif direction == 'r':
        Rotation_Delta(flight, 1, 0, int(angle * 100), ts, emergency)


def Yaw2(flight, direction, angle, ts=0, emergency=False):
    '''
    Rotate the flight's heading to the `angle` specified angle according to the `direction`

    *Parameters*:

    * `flight` - a `Flight` object
    * `direction`, a string, 'l' represents ccw and 'r' represents cw. 
    * `angel` - the angle in centi-degree, 0 - 35900
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    if angle == 360:
        angle = 359
    if angle == -360:
        angle = -359
    if direction == 'l':
        Rotation_Abs(flight, 0, 0, int(angle * 100), ts, emergency)
    elif direction == 'r':
        Rotation_Abs(flight, 1, 0, int(angle * 100), ts, emergency)


def WaitUntilReachYaw(flight, yaw, timeout=0):
    start = GetCurMs()
    yaw = yaw % 360.0
    while True:
        if (timeout > 0) and (GetCurMs() - start > timeout):
            return False
        pos = ReadPosition(flight)
        if pos == None:
            return False
        _, _, _, cur_yaw = pos
        if abs(cur_yaw - yaw) < 200:
            return True
        Delay(200)


def ReachYaw(flight, direction, angle, ts=0, online=False, timeout=0):
    if direction == 'l':
        ReachAngle(flight, 0, 0, int(-angle * 100), ts)
    elif direction == 'r':
        ReachAngle(flight, 0, 0, int(angle * 100), ts)
        # if online:
    #    WaitUntilReachYaw(flight, yaw, timeout)
    # else:
    return True


def ReachDeltaYaw(flight, direction, angle, ts=0, online=False, timeout=0):
    t = 0
    if ts == 0:
        _, _, _, cur_yaw = ReadPosition(flight)

    if abs(angle) >= 180:
        MaxAngularRate(flight, 120, ts)
        T = (abs(angle) / 120) * 1000

        while t < T:
            # print("%d/%d" % (t, T))
            da = angle / (T / 200)
            t += 200
            if direction == 'l':
                ReachAngleDelta(flight, 0, 0, int(-da * 100), ts + t)
            elif direction == 'r':
                ReachAngleDelta(flight, 0, 0, int(da * 100), ts + t)
            Delay(200)
    else:
        if direction == 'l':
            ReachAngleDelta(flight, 0, 0, int(-angle * 100), ts)
        elif direction == 'r':
            ReachAngleDelta(flight, 0, 0, int(angle * 100), ts)

    if online:
        return WaitUntilReachYaw(flight, cur_yaw + angle, timeout)
    else:
        return True


#
# flight, the flight instance
#
def Hover(flight, ts=0, emergency=False):
    '''
    Make the flight hover

    *Parameters*:

    * `flight` - a `Flight` object
    * `ts` - timestamp, 0 by default. Use 0 in online mode, use timestamp in offline mode
    * `emergency` - False by default, send emergency disarm command if the copters has already been running your scripts if set it as True.
    '''
    Displacement_Delta(flight, 0, 0, 0, ts, emergency)


def MotorPWM(flight, index, duty, ts=0, emergency=False):
    '''
    Motors test
    '''
    pwm = 65535 * duty
    MotorSpeed(flight, index, int(pwm), ts, emergency)


def MotorsPWM(flight, duty, ts=0, emergency=False):
    '''
    Motors test, all
    '''
    MotorPWM(flight, 4, duty, ts, emergency)


'''    
if __name__ == '__main__':
    pass
'''
