"""
gtrfs 兼容层 — 让 pyfii/官方软件生成的代码直接在 fwfii 上运行
==============================================================
pyfii 生成的 offlineExcuteScript.py 使用 gtrfs 命名空间:
    from gtrfs.fc import *
    from gtrfs.utils import *
    from gtrfs.led import *

本模块提供完全兼容的映射，只需将 import 改为:
    from fwfii.gtrfs_compat import *

或直接 monkey-patch:
    import fwfii.gtrfs_compat as gtrfs
"""
from __future__ import division, absolute_import, print_function

# ── fc 映射 ──
from fwfii.fc import Flight, Arm, Disarm, Takeoff, Land, Stop
from fwfii.fc.basic import (
    Move2, Move2Marker,
    Forward, Backward, Left, Right, Up, Down, Hover,
    Yaw, Yaw2, Flip, Nod,
    MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ, MaxAngularRate,
    SetFlightMode, ProgrammingMode, PlanningMode,
    MissionStart, MissionContinue, MissionPause,
    DelayLaunch, CancelLaunch,
    AddMark, ReadMarker, ReadPosition,
    SimpleHarmonic, SimpleHarmonic2, CylindricalSpiral,
    RoundInAir, MovewHeading, Reach, ReachDelta,
    ReachMarker, ReachYaw, ReachDeltaYaw,
    MotorPWM, MotorsPWM,
    Clamp, Magnet,
)
from fwfii.fc.advanced import (
    RTL, Reset, PowerOff,
    RequestVersion, RequestPosition, RequestBatteryCurrent,
    RequestFlightMode, RequestSerialNumber, RequestType,
    RequestAddress, RequestSensorState,
    Transfer, End_Transfer, End_Transfer2,
    Upgrade_LED, Upgrade_LED2, Upgrade_FC, Upgrade_RK,
    HeartBeatData, HeartBeatEnable,
    GenLsEnd, GenPosfile,
    Start, End,
    SetOrigin, SetBase, SetPoint,
    RequestOrigin, RequestBase, RequestPoint, RequestGrid,
    SetLaunchTime, RequestLaunchTime,
    ConnectionStatus,
)

# ── LED 映射 ──
from fwfii.led.lamp import (
    AllOn, AllOff, AllBlink, AllBreath,
    BodyOn, BodyOff, BodyBlink, BodyBreath,
    MotorOn, MotorOff, MotorBlink, MotorBreath, MotorHorse,
)

# ── utils 映射 ──
from fwfii.utils import Delay, GetCurMs, GetCurTime, GetCurUs

# ── MoveDelta: pyfii 用的相对位移指令 ──
from fwfii.fc.basic import Displacement_Delta as _Displacement_Delta

def MoveDelta(flight, dx, dy, dz, ts=0, emergency=False):
    """
    相对位移 — 与 gtrfs/pyfii 完全兼容

    Parameters:
        flight: Flight 对象
        dx, dy, dz: 相对位移 (cm)
        ts: 时间戳
    """
    _Displacement_Delta(flight, int(dy * 100), int(dx * 100), int(dz * 100),
                        ts, emergency)

# ── 常量 ──
BUZZER_MODE_ATOMIC = 0
BUZZER_MODE_SPEC1 = 1
LED_MODE_SINGLE = 0
LED_MODE_MULTI = 1
LED_MODE_SINGLE_ON = 2
LED_MODE_BLINK_FAST = 3
LED_MODE_BLINK_SLOW = 4
LED_MODE_SEQ = 5

# ── 颜色 ──
RED    = 0xFF0000
GREEN  = 0x00FF00
BLUE   = 0x0000FF
YELLOW = 0xFFFF00
CYAN   = 0x00FFFF
PURPLE = 0xFF00FF
WHITE  = 0xFFFFFF
ORANGE = 0xFF8000
PINK   = 0xFF0080

def convert_gtrfs_script(src_path, dst_path=None):
    """
    将 gtrfs/官方软件生成的脚本转换为 fwfii 兼容格式。

    替换 import 行:
        from gtrfs.fc   import *  →  from fwfii.gtrfs_compat import *
        from gtrfs.led  import *   →  (已包含在 gtrfs_compat 中)
        from gtrfs.utils import *  →  (已包含在 gtrfs_compat 中)

    Parameters:
        src_path: gtrfs 生成的脚本路径 (webCodeAll.py / offlineExcuteScript.py)
        dst_path: 输出路径 (默认覆盖源文件)
    """
    with open(src_path, 'r', encoding='utf-8') as f:
        code = f.read()

    code = code.replace('from gtrfs.fc import *',
                        'from fwfii.gtrfs_compat import *')
    code = code.replace('from gtrfs.led import *', '')
    code = code.replace('from gtrfs.utils import *', '')

    if dst_path is None:
        dst_path = src_path

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(code)

    return dst_path
