#
# Flight Code
#

from __future__ import division, absolute_import, print_function
from fwfii.atom import failsSafePack
from fwfii.utils import GetCurTime


class Flight:
    '''
    Create a Flight with the specified id, once created, it will send the heartbeat and position request commands to the copter automatically.

    *Parameters*:
        
    * `id` - an identifier to represent the copter, defaultly it is named by your self following the rules of naming. 
        * `id = group * 1000 + number`,  **Notice that** the number and group **MUST** be less than `255`, because the default IP address consists of the id, is `192.168.group.number`.
        * for example, if the group is `1` and number is `200`, the id equals `1200`, IP address is `192.168.1.200`.

    *Returns*: A `Flight` object
    '''
    control_mode = ("STABILIZE", "ACRO", "ALT_HOLD", "AUTO", \
                    "GUIDED", "LOITER", "RTL", "CIRCLE", "N/A", "LAND", \
                    "N/A", "DRIFT", "N/A", "SPORT", "FLIP", "AUTOTUNE", "POSHOLD", \
                    "BRAKE", "THROW", "AVOID_ADSB", "GUIDED_NOGPS")
    gps_status = ("NO_GPS", "NO_FIX", "FIX_2D", "FIX_3D", \
                 "3D_DGPS", "RTK_FLOAT", "RTK_FIXED")
    def __init__(self, uavid):
        from .heartbeat import HeartBeat
        self._uavid = uavid
        self.reset()
        HeartBeat.addFlight(self)

    def __str__(self):
        return str(self.uavid)

    def reset(self):
        self._fcstatus = "N/A"
        self._flightmode = "N/A"
        self._lastBeatTime = GetCurTime()
        self._x = 0
        self._y = 0
        self._z = 0
        self._yaw = 0
        self._maplat = 0
        self._maplng = 0
        self._rtkbaselat = 0
        self._rtkbaselng = 0
        self._rtkbasealt = 0
        self._launchutc = 'N/A'
        self._gpsstatus = "NO_GPS"
        self._voltage = 0
        self._prev_z = 0

    @property
    def uavid(self):
        return self._uavid

    @uavid.setter
    def uavid(self, value):
        self._uavid = value
        
    @property
    def lastBeatTime(self):
        return self._lastBeatTime

    @lastBeatTime.setter
    def lastBeatTime(self, value):
        self._lastBeatTime = value

    @property
    def position(self):
        return (self._x * 100, self._y * 100, self._z * 100, self._yaw * 100)

    @position.setter
    def position(self, value):
        self._y, self._x, self._z, self._yaw = value[0] * 0.01, value[1] * 0.01, value[2] * 0.01, value[3] * 0.01

    def set_init_pos(self, x, y):
        """Set the physical takeoff position on carpet (cm)."""
        self._init_x = x
        self._init_y = y
        self._pos_locked = False
        self._landing = False
        self._prev_z = 0
        self._land_x = None
        self._land_y = None
        self._last_good_x = None
        self._last_good_y = None

    @property
    def display_position(self):
        """Position for display — masks ghost XY with init/last-good values.

        - On ground:      init XY (before 1st flight) or last landing XY
        - Taking off:     init XY until position lock acquired
        - Flying locked:  real XY
        - Landing:        XY frozen at landing-trigger moment (rapid descent)
        """
        real = self.position  # (x, y, z, yaw) cm
        on_ground = abs(real[2]) <= 5
        dz = real[2] - self._prev_z

        if not hasattr(self, '_init_x'):
            self._prev_z = real[2]
            return real

        # ── detect position lock ──
        if not self._pos_locked and not on_ground:
            airborne = real[2] > 15
            dist_from_ghost = ((real[0] - 22)**2 + (real[1] - 24)**2)**0.5
            if airborne or dist_from_ghost > 20:
                self._pos_locked = True

        # detect landing: rapid descent (>15cm drop) while locked
        if self._pos_locked and not self._landing and dz < -15:
            self._landing = True
            self._land_x = real[0]
            self._land_y = real[1]

        # ── exit landing on ascent back to altitude ──
        if self._landing and real[2] > 30:
            self._landing = False

        # ── save last good XY while flying stable ──
        if self._pos_locked and not self._landing and real[2] > 10:
            self._last_good_x = real[0]
            self._last_good_y = real[1]

        # ── choose display XY ──
        if on_ground:
            if self._pos_locked:
                self._pos_locked = False
                self._landing = False
            x = self._last_good_x if self._last_good_x is not None else self._init_x
            y = self._last_good_y if self._last_good_y is not None else self._init_y
        elif self._landing:
            x, y = self._land_x, self._land_y
        elif not self._pos_locked:
            x, y = self._init_x, self._init_y
        else:
            x, y = real[0], real[1]

        self._prev_z = real[2]
        return (x, y, real[2], real[3])

    @property
    def fcstatus(self):
        return self._fcstatus

    @fcstatus.setter
    def fcstatus(self, value):
        self._fcstatus = value

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._voltage = value

    @property
    def flightmode(self):
        return self._flightmode

    @flightmode.setter
    def flightmode(self, value):
        self._flightmode = value

    @property
    def gpsstatus(self):
        return self._gpsstatus

    @gpsstatus.setter
    def gpsstatus(self, value):
        self._gpsstatus = value

    @property
    def maporigin(self):
        return (self._maplat, self._maplng)

    @maporigin.setter
    def maporigin(self, value):
        self._maplat, self._maplng = value[0] * 1e-7, value[1] * 1e-7

    @property
    def launchutc(self):
        return self._launchutc

    @launchutc.setter
    def launchutc(self, value):
        import datetime
        s = value / 1000.0
        self._launchutc = datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%d %H:%M:%S.%f')

    @property
    def rtkbaseloc(self):
        return (self._rtkbaselat, self._rtkbaselng, self._rtkbasealt)

    @rtkbaseloc.setter
    def rtkbaseloc(self, value):
        self._rtkbaselat, self._rtkbaselng, self._rtkbasealt = value

    def obtainStatus(self, status):
        failsafe = failsSafePack(status)
 
        if failsafe.battery_clow:
            self.fcstatus = "Dead Battery"
        elif ((failsafe.acc_health) or (failsafe.gyro_health) or \
             failsafe.acc_not_cal or failsafe.acc_inconsist or \
             failsafe.gyro_inconsist or failsafe.gyro_cal_fail):
            self.fcstatus = "Bad IMU"
        elif ((failsafe.mag_health) or failsafe.mag_yaw_error or \
             failsafe.compass_variance or failsafe.mag_not_cal or \
             failsafe.mag_offset_high or failsafe.mag_length_fail or \
             failsafe.mag_inconsist):
            self.fcstatus = "Bad Mag"
        elif (failsafe.baro_health or failsafe.range_finder):
            self.fcstatus = "Bad Baro"
        elif failsafe.gps_health or  failsafe.need_3d_fix or \
             failsafe.high_gps_hdop or failsafe.gps_vert_vel_error or \
             failsafe.gps_speed_error or failsafe.gps_horiz_error or \
             failsafe.gps_numstats or failsafe.gps_drift or \
             failsafe.gps_bad_vert_vel or failsafe.gps_bad_hor_vel or \
             failsafe.gps_bad_hdop:
            self.fcstatus = "Bad GPS"
        elif (failsafe.m1 or failsafe.m2 or failsafe.m3 or failsafe.m4):
            self.fcstatus = "Bad Motor"
        elif (not failsafe.postion_ok):
            self.fcstatus = "pos not ok"
        elif (failsafe.home_variance):
            self.fcstatus = "Bad Homevariance"
        elif (failsafe.leaning):
            self.fcstatus = "Leaning"
        elif (not failsafe.pre_check_ok):
            self.fcstatus = "prearm check fail"
        else:
            self.fcstatus = "Good"

        #print(failsafe.mode, failsafe.gps_status)
        self.flightmode = Flight.control_mode[failsafe.mode]
        self.gpsstatus  = Flight.gps_status[failsafe.gps_status]

        if self.gpsstatus == "NO_FIX":
            self.maporigin = (0, 0)

    def printInfo(self):
        dp = self.display_position
        x = dp[1]
        y = dp[0]
        z = dp[2]
        if self.maporigin[0] == 0 and self.maporigin[1] == 0:
            x *= 1e-7
            y *= 1e-7
        
        return [self.flightmode, int(self.voltage), self.gpsstatus, self.fcstatus, x, y, z, self.position[3], self.maporigin]
    
   
        