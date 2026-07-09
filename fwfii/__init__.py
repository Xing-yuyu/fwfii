"""
fwfii — Fii Drone Flight Control SDK
=====================================

一键导入::

    from fwfii import connect, disconnect, Flight
    from fwfii import Arm, Takeoff, Land, Move2, Delay
    from fwfii import AllOn, AllOff, RED, GREEN, BLUE
"""
from __future__ import division, absolute_import, print_function

# ── 快捷操作 ──
from .quick import connect, disconnect, plan, deliver, mission_start

# ── 飞行核心 ──
from .fc import Flight
from .fc.basic import (
    Arm, Disarm, Takeoff, Land, Stop,
    Move2, Forward, Backward, Left, Right, Up, Down, Hover,
    Yaw, Yaw2, Flip, Nod,
    MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ, MaxAngularRate,
    ProgrammingMode, PlanningMode,
    MissionStart, MissionContinue, MissionPause,
    SetFlightMode,
    AddMark, Move2Marker, ReadPosition,
    SimpleHarmonic, CylindricalSpiral, RoundInAir, MovewHeading,
    Reach, ReachDelta, ReachMarker, ReachYaw, ReachDeltaYaw,
)
from .fc.advanced import (
    RTL, Reset, PowerOff, DelayLaunch,
    RequestVersion, RequestPosition, RequestBatteryCurrent,
    RequestFlightMode, RequestSerialNumber,
)

# ── LED 灯光 ──
from .led.lamp import (
    AllOn, AllOff, AllBlink, AllBreath,
    BodyOn, BodyOff, BodyBlink, BodyBreath,
    MotorOn, MotorOff, MotorBlink, MotorBreath, MotorHorse,
)

# ── 工具 ──
from .utils import Delay, GetCurMs, GetCurTime

# ── 遥测 / 音乐 ──
from .utils.logger import start_log, stop_log, is_logging, FlightLogger
from .utils.music import (
    load_music, play_music, stop_music,
    pause_music, unpause_music,
    set_music_volume, is_music_playing, wait_music,
)

# ── 常用颜色常量 ──
RED    = 0xFF0000
GREEN  = 0x00FF00
BLUE   = 0x0000FF
YELLOW = 0xFFFF00
CYAN   = 0x00FFFF
PURPLE = 0xFF00FF
WHITE  = 0xFFFFFF
ORANGE = 0xFF8000
PINK   = 0xFF0080
