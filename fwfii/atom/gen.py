#/usr/bin/env python
from __future__ import division, absolute_import, print_function
import ctypes

def crc(stream):
    crc = 0

    for byte in stream:
        for bit in range(7, -1, -1):
            if crc & pow(2, 7) != 0:
                crc = (crc << 1) & 0xFF
                crc = (crc ^ 0x07) & 0xFF
            else:
                crc = (crc << 1) & 0xFF

            if byte & pow(2, bit) != 0:
                crc = (crc ^ 0x07) & 0xFF

    return crc

class _zigbeeHeader(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("id",      ctypes.c_uint8,     8),
                 ("length",  ctypes.c_uint8,     8),
                 ("counter", ctypes.c_uint16,    15),
                 ("dir",     ctypes.c_uint16,    1),
                 ("address", ctypes.c_uint8,     8),
                 ("group",   ctypes.c_uint8,     8) ]

class _packHeader(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("id",      ctypes.c_uint8,     8),
                 ("crc",     ctypes.c_uint8,     8),
                 ("ts",      ctypes.c_uint32,    32),
                 ("reg",     ctypes.c_uint16,    12),
                 ("group",   ctypes.c_uint16,    3),
                 ("rw",      ctypes.c_uint16,    1) ]


class flightPayload(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("state",   ctypes.c_uint32,     8),
                 ("z",       ctypes.c_uint32,     24),
                 ("x",       ctypes.c_uint32,     32),
                 ("y",       ctypes.c_uint32,     32),
                 ("res",     ctypes.c_uint8 * 12) ]

    def __init__(self, state, x, y, z, vx = 0, vy = 0, vz = 0):
        self.state = state
        self.z = z
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.vz = vz

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))

class rcPayload(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("roll",   ctypes.c_uint16,     16),
                 ("pitch",       ctypes.c_uint16,     16),
                 ("thr",       ctypes.c_uint16,     16),
                 ("yaw",       ctypes.c_uint16,     16),
                 ("res",     ctypes.c_uint8 * 16) ]

    def __init__(self, roll, pitch, thr, yaw):
        self.roll = roll
        self.pitch = pitch
        self.thr = thr
        self.yaw= yaw

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))        



class dummyPayload(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("bytes",   ctypes.c_uint8 * 24) ]    

class uavPackPayload(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("bytes",   ctypes.c_uint8 * 13) ]   

class otaPayload(uavPackPayload):
    def __init__(self, filesize):
        self.bytes[0] = (filesize & 0xFF)
        self.bytes[1] = (filesize & 0xFF00) >> 8
        self.bytes[2] = (filesize & 0xFF0000) >> 16
        self.bytes[3] = (filesize & 0xFF000000) >> 24    

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))       


LED_MODE_SINGLE         = 0
LED_MODE_MULTI          = 1
LED_MODE_SINGLE_ON      = 2
LED_MODE_BLINK_FAST     = 3
LED_MODE_BLINK_SLOW     = 4
LED_MODE_SEQ            = 5

class lightPayload(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("id",         ctypes.c_uint8, 4), 
                 ("counter",    ctypes.c_uint8, 4), 
                 ("mode",       ctypes.c_uint8, 8),
                 ("reserved",   ctypes.c_uint8, 8),
                 ("red",        ctypes.c_uint8, 8),
                 ("green",      ctypes.c_uint8, 8),
                 ("blue",       ctypes.c_uint8, 8) ]

    COUNTER = 0
    def __init__(self, id, mode, color):
        self.id       = id
        self.counter  = lightPayload.COUNTER // 4
        lightPayload.COUNTER = lightPayload.COUNTER + 1
        if lightPayload.COUNTER == 12:
            lightPayload.COUNTER = 0
        self.mode     = mode
        self.red      = (color & 0xFF0000) >> 16
        self.green    = (color & 0x00FF00) >> 8
        self.blue     = (color & 0x0000FF)

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))

class lightGroup(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("light",         lightPayload * 4) ]

    def __init__(self, l1, l2, l3, l4):
        if l1 != None:
            self.light[0] = l1
        if l2 != None:
            self.light[1] = l2
        if l3 != None:
            self.light[2] = l3
        if l4 != None:
            self.light[3] = l4

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))

class dutyABPayload(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("id",         ctypes.c_uint8, 4), 
                 ("counter",    ctypes.c_uint8, 4), 
                 ("DUTYA",      ctypes.c_uint32, 32),
                 ("DUTYB",      ctypes.c_uint32, 32),
                 ("reserved",   ctypes.c_uint8 * 15 )]

    def __init__(self, dutyA, dutyB):
        self.counter  = 1
        lightPayload.COUNTER = 8
        self.DUTYA = dutyA
        self.DUTYB = dutyB

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))

BUZZER_MODE_ATOMIC  = 0
BUZZER_MODE_SPEC1   = 1
BUZZER_MODE_SPEC2   = 2
BUZZER_MODE_SPEC3   = 3
BUZZER_MODE_SPEC4   = 4
BUZZER_MODE_SPEC5   = 5
BUZZER_MODE_SPEC6   = 6

class buzzerPayload(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [ ("mode",       ctypes.c_uint8,  8), 
                 ("fre",        ctypes.c_uint16, 16), 
                 ("duty",       ctypes.c_uint8,  8),
                 ("on_off",     ctypes.c_uint8,  8),
                 ("reserved",   ctypes.c_uint8 * 19)]

    def __init__(self, mode, fre, duty, on_off):
        self.mode    = mode
        self.fre     = fre
        self.duty    = duty
        self.on_off  = self.on_off 

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))

class wifiPack(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("pack_header",     _packHeader),
                 ("payload",         ctypes.c_uint8 * ctypes.sizeof(flightPayload)) ]

    def __init__(self, ts, reg, rw, payload):
        self.pack_header.id        = 0xD5
        self.pack_header.ts        = ts
        self.pack_header.reg       = reg
        self.pack_header.rw        = rw
        self.pack_header.crc       = 0
        self.payload               = (ctypes.c_uint8 * ctypes.sizeof(self.payload)).from_buffer_copy((payload))
        self.pack_header.crc       = crc((ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self))[2 : ctypes.sizeof(self)]) 

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))  

class zigbeePack(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("zigbee_header",   _zigbeeHeader),
                 ("payload",         ctypes.c_uint8 * 32),
                 ("res",             ctypes.c_uint8),
                 ("crc",             ctypes.c_uint8) ]

    COUNTER  = 0
    def __init__(self, flight, payload):
        zigbeePack.COUNTER += 1
        self.zigbee_header.id          = 0xDD
        self.zigbee_header.length      = ctypes.sizeof(zigbeePack) - 3
        self.zigbee_header.dir         = 1
        self.zigbee_header.counter     = zigbeePack.COUNTER
        self.zigbee_header.address     = flight.uavid % 1000
        self.zigbee_header.group       = flight.uavid // 1000
        self.payload                   = (ctypes.c_uint8 * ctypes.sizeof(self.payload)).from_buffer_copy((payload))
        self.crc                       = crc((ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self))[1 : ctypes.sizeof(self) - 1]) 

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))


class uavPack(ctypes.LittleEndianStructure):
    _pack_   = 1
    _fields_ = [ ("zigbee_header",   _zigbeeHeader),
                 ("reg",     ctypes.c_uint16,    12),
                 ("group",   ctypes.c_uint16,    3),
                 ("rw",      ctypes.c_uint16,    1),
                 ("payload", ctypes.c_uint8 * 13),
                 ("crc",     ctypes.c_uint8) ]

    def __init__(self, flight, reg, rw, payload):
        zigbeePack.COUNTER += 1
        self.zigbee_header.id          = 0xDD
        self.zigbee_header.length      = ctypes.sizeof(uavPack) - 3
        self.zigbee_header.dir         = 1
        self.zigbee_header.counter     = zigbeePack.COUNTER                 
        self.zigbee_header.address     = flight.uavid % 1000
        self.zigbee_header.group       = flight.uavid // 1000
        self.reg                       = reg
        self.rw                        = rw
        self.payload                   = (ctypes.c_uint8 * ctypes.sizeof(self.payload)).from_buffer_copy((payload))
        self.crc                       = crc((ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self))[1 : ctypes.sizeof(self) - 1]) 
    
    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))

    def __repr__(self):
        return ''.join('{:02x} '.format(x) for x in (ctypes.c_uint8 * ctypes.sizeof(self)).from_buffer_copy((self)))    

class failsSafePack(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [    ("res",           ctypes.c_uint8,     8), #1
                    ("pre_check_ok",  ctypes.c_uint8,     1),
                    ("postion_ok",    ctypes.c_uint8,     1),
                    ("marker_ok",     ctypes.c_uint8,     1),
                    ("gps_status",    ctypes.c_uint8,     3), 
                    ("reserved1",     ctypes.c_uint8,     2), #2
                    ("mode",          ctypes.c_uint8,     6), #3
                    ("armdisarm",     ctypes.c_uint8,     1), 
                    ("usb",           ctypes.c_uint8,     1),
                    ("acc_health",    ctypes.c_uint8,     1), 
                    ("gyro_health",   ctypes.c_uint8,     1),
                    ("baro_health",   ctypes.c_uint8,     1),
                    ("mag_health",    ctypes.c_uint8,     1),
                    ("sonar_health",  ctypes.c_uint8,     1),
                    ("optical_health",ctypes.c_uint8,     1),
                    ("gps_health",    ctypes.c_uint8,     1),
                    ("stereo_camera_health", ctypes.c_uint8, 1),#4
                    ("m1",            ctypes.c_uint8,     2),
                    ("m2",            ctypes.c_uint8,     2),
                    ("m3",            ctypes.c_uint8,     2),
                    ("m4",            ctypes.c_uint8,     2), #5
                    ("rc_lost",       ctypes.c_uint8,     1),
                    ("battery_clow",   ctypes.c_uint8,     1),
                    ("crash_flag",    ctypes.c_uint8,     1),
                    ("force_disarm_flag", ctypes.c_uint8, 1),
                    ("angle_big_flag",ctypes.c_uint8,     1),
                    ("battery_low",   ctypes.c_uint8,     1),
                    ("reserved2",     ctypes.c_uint8,     2), #6
                    ("crash_total_number1", ctypes.c_uint8, 8), #7
                    ("crash_total_number2", ctypes.c_uint8, 8), #8
                    ("nav_checks",    ctypes.c_uint8,     1),
                    ("gyro_cal_fail", ctypes.c_uint8,      1),
                    ("gps_vert_vel_error", ctypes.c_uint8, 1),
                    ("gps_speed_error", ctypes.c_uint8,    1),
                    ("gps_horiz_error", ctypes.c_uint8,    1),
                    ("mag_yaw_error", ctypes.c_uint8,      1),
                    ("gps_numstats",  ctypes.c_uint8,      1),
                    ("need_3d_fix",   ctypes.c_uint8,      1), #9
                    ("compass_variance", ctypes.c_uint8,   1),
                    ("home_variance", ctypes.c_uint8,      1),
                    ("high_gps_hdop", ctypes.c_uint8,      1),
                    ("baro_alt",      ctypes.c_uint8,      1),
                    ("mag_not_cal",   ctypes.c_uint8,      1),
                    ("mag_offset_high", ctypes.c_uint8,    1),
                    ("mag_length_fail", ctypes.c_uint8,    1),
                    ("mag_inconsist", ctypes.c_uint8,      1),# 10
                    ("acc_not_cal",   ctypes.c_uint8,      1),
                    ("battery_low1",   ctypes.c_uint8,      1),
                    ("range_finder",  ctypes.c_uint8,      1),
                    ("acc_inconsist", ctypes.c_uint8,      1),
                    ("gyro_inconsist", ctypes.c_uint8,     1),
                    ("leaning",       ctypes.c_uint8,      1),
                    ("gps_drift",      ctypes.c_uint8,      1),
                    ("gps_bad_vert_vel",ctypes.c_uint8,      1),#11
                    ("gps_bad_hor_vel",ctypes.c_uint8,      1),
                    ("gps_bad_hdop",   ctypes.c_uint8,      1),
                    ("fence_outside",    ctypes.c_uint8,      1),
                    ("fence_require_pos",ctypes.c_uint8,      1),
                    ("gyro_still",       ctypes.c_uint8,      1),
                    ("reserved4",     ctypes.c_uint8,      3), #12
                    ("arm_action",    ctypes.c_uint8,       7),
                    ("arm_on",        ctypes.c_uint8,       1) ] #13

    def __init__(self, s):
        pass
        
    def __new__(cls, buf):
        return cls.from_buffer_copy(buf)  

    def __str__(self):
        return ctypes.string_at(ctypes.addressof(self), ctypes.sizeof(self))                    

if __name__ == '__main__':
    '''
    print(ctypes.sizeof(_zigbeeHeader)     )
    print(ctypes.sizeof(_packHeader))
    print(ctypes.sizeof(flightPayload))
    print(ctypes.sizeof(zigbeePack))

    wp = flightPayload(0, 1, 2, 3)
    print((wp))
    print(repr(wp))

    wfp = wifiPack(1, 10, 1, wp)
    print(repr(wfp))

    from fwfii.fc import Flight
    zp = zigbeePack(Flight(1001), wfp)
    print(repr(zp))

    lpg = lightGroup(lightPayload(0, 1, 2), None, lightPayload(0, 1, 2), lightPayload(0, 1, 2))
    wfp = wifiPack(3, 11, 2, lpg)
    print(repr(wfp))

    bp = buzzerPayload(1, 2, 3, 4)
    wfp = wifiPack(2, 12, 3, bp)
    print(repr(wfp))
    '''
    print(ctypes.sizeof(uavPack))
