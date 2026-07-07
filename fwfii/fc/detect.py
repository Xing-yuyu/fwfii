#!/usr/bin/env python
from __future__ import division, absolute_import, print_function
from .basic import *
from fwfii.utils import Delay, GetCurMs
from math import sqrt, sin, cos, pi
import traceback

# fSizeLW = 15
fSizeLW = 0
fSizeH = 10

fLimitLW = 80
fLimitH = 0
fDisSumLW = fSizeLW + fLimitLW
fDisSumH = fSizeH + fLimitH


def ReadObstacleX(obstacle):
    from .obstacle import cube
    for obj in cube.Obstacles:
        if obj.centroid == obstacle.centroid:
            print(obj.centroid[0])
            return obj.centroid[0]
    return 0


def ReadObstacleY(obstacle):
    from .obstacle import cube
    for obj in cube.Obstacles:
        if obj.centroid == obstacle.centroid:
            print(obj.centroid[1])
            return obj.centroid[1]
    return 0


def ReadObstacleZ(obstacle):
    from .obstacle import cube
    for obj in cube.Obstacles:
        if obj.centroid == obstacle.centroid:
            print(obj.centroid[2])
            return obj.centroid[2]
    return 0


def ReadObstacleL(obstacle):
    from .obstacle import cube
    for obj in cube.Obstacles:
        if obj.centroid == obstacle.centroid:
            print(obj.length)
            return obj.length
    return 0


def ReadObstacleW(obstacle):
    from .obstacle import cube
    for obj in cube.Obstacles:
        if obj.centroid == obstacle.centroid:
            print(obj.width)
            return obj.width
    return 0


def ReadObstacleH(obstacle):
    from .obstacle import cube
    for obj in cube.Obstacles:
        if obj.centroid == obstacle.centroid:
            print(obj.height)
            return obj.height
    return 0


def DetectMarker(flight, obstacle=None, dx=-1, dy=-1, dz=-1):
    if obstacle == None:
        if DetectMarkerALL(flight) != None:
            return True
    else:
        from .obstacle import cube
        for obj in cube.Obstacles.keys():
            if obj == obstacle:
                objobstacle = cube.Obstacles[obj];
                break
        if dx == -1 and dy == -1 and dz == -1:
            value = DetectObjectDistance(flight, objobstacle)
            if value == None:
                return False
            if value[0] == None:
                print("error 1")
                return False
            else:
                print("dis:")
                print(value[0])
                if value[0] == 5:
                    return True
                else:
                    print(value[1])
                    if value[1] < fLimitLW:
                        return True
                    else:
                        return False
        else:
            pos = ReadPosition2(flight)
            if pos == None:
                return False
            distance = 0
            if pos[2] - dz > ReadObstacleH(obstacle):
                print("Z find")
                return True

            quadrant = GetQuadrant(pos, obstacle)
            if quadrant == None:
                return False

            if quadrant == 1:
                distance = ReadObstacleY(obstacle) - ReadObstacleW(obstacle) / 2 - pos[1] - dx
            elif quadrant == 2:
                distance = pos[0] - ReadObstacleL(obstacle) / 2 - ReadObstacleX(obstacle) - dy
            elif quadrant == 3:
                distance = pos[1] - ReadObstacleY(obstacle) - ReadObstacleW(obstacle) / 2 - dx
            elif quadrant == 4:
                distance = ReadObstacleX(obstacle) - pos[0] - ReadObstacleL(obstacle) / 2 - dy

            if distance <= 15:
                print("XY find")
                return True

    return False


def DetectMarkerALL(flight):
    pos = ReadPosition2(flight)
    if pos == None:
        return False
    from .obstacle import cube
    for obj in cube.Obstacles.keys():
        if DetectMarker(flight, obj):
            return True
    return False


def DetectOBJType(flight, objtype, dx=-1, dy=-1, dz=-1):
    from .obstacle import cube
    for obj in cube.Obstacles.keys():
        if cube.Obstacles[obj].objtype == objtype:
            if dx == -1 and dy == -1 and dz == -1:
                if DetectMarker(flight, obj):
                    return True
                else:
                    return False
            else:
                if DetectMarker(flight, obj, dx, dy, dz):
                    return True
                else:
                    return False
    return False


def CrashMarker(flight, obstacle=None):
    if obstacle == None:
        if DetectMarkerALL(flight) != None:
            return True
    else:
        from .obstacle import cube
        for obj in cube.Obstacles.keys():
            if obj == obstacle:
                objobstacle = cube.Obstacles[obj];
                break
        value = DetectObjectDistance(flight, objobstacle)
        if value == None:
            return False
        if value[0] == None:
            print("error 1")
            return False
        else:
            print("dis:")
            print(value[0])
            if value[0] == 5:
                return True
            else:
                print(value[1])
                if value[1] < 15:
                    return True
                else:
                    return False
    return False


def CrashOBJType(flight, objtype):
    from .obstacle import cube
    for obj in cube.Obstacles.keys():
        if cube.Obstacles[obj].objtype == objtype:
            if CrashMarker(flight, obj):
                return True
            else:
                return False
    return False


def CrashMarkerALL(flight):
    pos = ReadPosition2(flight)
    if pos == None:
        return False
    from .obstacle import cube
    for obj in cube.Obstacles.keys():
        if CrashMarker(flight, obj):
            return True
    return False


def GetQuadrant(fObj, bObj):
    value = 0

    try:
        x1 = ReadObstacleX(bObj) - ReadObstacleL(bObj) / 2
        x2 = ReadObstacleX(bObj) + ReadObstacleL(bObj) / 2
        y1 = ReadObstacleY(bObj) - ReadObstacleW(bObj) / 2
        y2 = ReadObstacleY(bObj) + ReadObstacleW(bObj) / 2

        a1 = (y2 - y1) / (x2 - x1)
        a2 = (y1 - y2) / (x2 - x1)

        b1 = ReadObstacleY(bObj) - a1 * ReadObstacleX(bObj)
        b2 = ReadObstacleY(bObj) - a2 * ReadObstacleX(bObj)

        if fObj[1] <= a1 * fObj[0] + b1:
            if fObj[1] <= a2 * fObj[0] + b2:
                value = 1
            elif fObj[1] > a2 * fObj[0] + b2:
                value = 2
        elif fObj[1] > a1 * fObj[0] + b1:
            if fObj[1] <= a2 * fObj[0] + b2:
                value = 4
            elif fObj[1] > a2 * fObj[0] + b2:
                value = 3

        return value



    except:
        return None


def DetectObjectDistance(flight, obstacle):
    try:
        pos = ReadPosition2(flight)

        print("pos = " + str(pos))

        distance = 0
        if pos[2] - fSizeH > ReadObstacleH(obstacle):
            return None

        quadrant = GetQuadrant(pos, obstacle)
        if quadrant == None:
            return None

        if quadrant == 1:
            distance = ReadObstacleY(obstacle) - ReadObstacleW(obstacle) / 2 - pos[1] - fSizeLW
        elif quadrant == 2:
            distance = pos[0] - ReadObstacleL(obstacle) / 2 - ReadObstacleX(obstacle) - fSizeLW
        elif quadrant == 3:
            distance = pos[1] - ReadObstacleY(obstacle) - ReadObstacleW(obstacle) / 2 - fSizeLW
        elif quadrant == 4:
            distance = ReadObstacleX(obstacle) - pos[0] - ReadObstacleL(obstacle) / 2 - fSizeLW

        if distance < 0:
            if pos[2] > ReadObstacleZ(obstacle) + ReadObstacleH(obstacle) / 2:
                distance = pos[2] - ReadObstacleH(obstacle)
                quadrant = 5

        retVal = [0, 0]

        retVal[0] = quadrant
        retVal[1] = distance

        print("distance = " + str(distance))
        print("quadrant = " + str(quadrant))

        return retVal


    except:
        traceback.print_exc()
        # print("DetectObjectDistance ex")
        return None


def DistanceMarkerOBJ(flight, obj=None):
    if object == None:
        return 0
    else:
        value = DetectObjectDistance(flight, obj)
        if value == None:
            return 0
        else:
            return value[1]


def DistanceMarker(flight, obj):
    value = DetectObjectDistance(flight, obj)
    if value == None:
        return 0
    else:
        return value[1]
