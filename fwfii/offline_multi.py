"""
离线多机任务模式 — 一个脚本编写全部无人机，自动拆分为独立脚本 + 项目结构
====================================================================

用法::

    from fwfii.offline_multi import MultiPlan

    mp = MultiPlan()
    mp.add_drone(71101, pos=(20, 20))
    mp.add_drone(71102, pos=(40, 20))
    mp.set_music("music.mp3")
    mp.set_carpet(80)

    # 一键构建: 统一脚本 → per-drone .py + .ls + project.json
    mp.build("unified_show.py", "./my_show")

编译输出::

    my_show/
    ├── project.json
    ├── scripts/
    │   ├── drone_71101.py
    │   └── drone_71102.py
    ├── 71101.ls
    └── 71102.ls
"""
from __future__ import division, absolute_import, print_function

import functools
import inspect
import json
import os
import struct
import sys
import traceback

from fwfii.fc import Flight
from fwfii.utils import Delay as _Delay


# ── 需要拦截的 API 函数列表 ──────────────────────

# 飞行控制 (fwfii.fc.basic) — 第一个参数是 Flight 对象
_FC_BASIC_FUNCTIONS = [
    'Arm', 'Disarm', 'Takeoff', 'Land', 'Stop',
    'Move2', 'Move2Marker',
    'Forward', 'Backward', 'Left', 'Right', 'Up', 'Down', 'Hover',
    'Yaw', 'Yaw2', 'Flip', 'Nod',
    'MaxVelXY', 'MaxVelZ', 'MaxAccXY', 'MaxAccZ', 'MaxAngularRate',
    'ProgrammingMode', 'PlanningMode',
    'MissionStart', 'MissionContinue', 'MissionPause',
    'SetFlightMode',
    'MoveDelta',
    'MotorPWM', 'MotorsPWM',
    'Clamp', 'Magnet',
    'SimpleHarmonic', 'SimpleHarmonic2', 'CylindricalSpiral',
    'RoundInAir', 'MovewHeading',
    'Reach', 'ReachDelta', 'ReachMarker', 'ReachYaw', 'ReachDeltaYaw',
]

# LED 灯光 (fwfii.led.lamp) — 第一个参数是 Flight 对象
_LAMP_FUNCTIONS = [
    'AllOn', 'AllOff', 'AllBlink', 'AllBreath',
    'BodyOn', 'BodyOff', 'BodyBlink', 'BodyBreath',
    'MotorOn', 'MotorOff', 'MotorBlink', 'MotorBreath',
    'MotorHorse',
]

# 全局函数 — 不在 per-drone 拆分中生成，但影响时间轴
_GLOBAL_FUNCTIONS = ['Delay']

# 生成 .py 时需要导入的模块 (按使用的命令动态收集)
_CMD_IMPORT_MAP = {
    # fc.basic
    'Arm': 'fwfii.fc.basic',
    'Disarm': 'fwfii.fc.basic',
    'Takeoff': 'fwfii.fc.basic',
    'Land': 'fwfii.fc.basic',
    'Stop': 'fwfii.fc.basic',
    'Move2': 'fwfii.fc.basic',
    'Move2Marker': 'fwfii.fc.basic',
    'Forward': 'fwfii.fc.basic',
    'Backward': 'fwfii.fc.basic',
    'Left': 'fwfii.fc.basic',
    'Right': 'fwfii.fc.basic',
    'Up': 'fwfii.fc.basic',
    'Down': 'fwfii.fc.basic',
    'Hover': 'fwfii.fc.basic',
    'Yaw': 'fwfii.fc.basic',
    'Yaw2': 'fwfii.fc.basic',
    'Flip': 'fwfii.fc.basic',
    'Nod': 'fwfii.fc.basic',
    'MaxVelXY': 'fwfii.fc.basic',
    'MaxVelZ': 'fwfii.fc.basic',
    'MaxAccXY': 'fwfii.fc.basic',
    'MaxAccZ': 'fwfii.fc.basic',
    'MaxAngularRate': 'fwfii.fc.basic',
    'ProgrammingMode': 'fwfii.fc.basic',
    'PlanningMode': 'fwfii.fc.basic',
    'MissionStart': 'fwfii.fc.basic',
    'MissionContinue': 'fwfii.fc.basic',
    'MissionPause': 'fwfii.fc.basic',
    'SetFlightMode': 'fwfii.fc.basic',
    'MoveDelta': 'fwfii.fc.basic',
    'MotorPWM': 'fwfii.fc.basic',
    'MotorsPWM': 'fwfii.fc.basic',
    'Clamp': 'fwfii.fc.basic',
    'Magnet': 'fwfii.fc.basic',
    'SimpleHarmonic': 'fwfii.fc.basic',
    'SimpleHarmonic2': 'fwfii.fc.basic',
    'CylindricalSpiral': 'fwfii.fc.basic',
    'RoundInAir': 'fwfii.fc.basic',
    'MovewHeading': 'fwfii.fc.basic',
    'Reach': 'fwfii.fc.basic',
    'ReachDelta': 'fwfii.fc.basic',
    'ReachMarker': 'fwfii.fc.basic',
    'ReachYaw': 'fwfii.fc.basic',
    'ReachDeltaYaw': 'fwfii.fc.basic',
    'AddMark': 'fwfii.fc.basic',
    'ReadMarker': 'fwfii.fc.basic',
    'ReadPosition': 'fwfii.fc.basic',
    # led.lamp
    'AllOn': 'fwfii.led.lamp',
    'AllOff': 'fwfii.led.lamp',
    'AllBlink': 'fwfii.led.lamp',
    'AllBreath': 'fwfii.led.lamp',
    'BodyOn': 'fwfii.led.lamp',
    'BodyOff': 'fwfii.led.lamp',
    'BodyBlink': 'fwfii.led.lamp',
    'BodyBreath': 'fwfii.led.lamp',
    'MotorOn': 'fwfii.led.lamp',
    'MotorOff': 'fwfii.led.lamp',
    'MotorBlink': 'fwfii.led.lamp',
    'MotorBreath': 'fwfii.led.lamp',
    'MotorHorse': 'fwfii.led.lamp',
}

# 颜色常量
_COLOR_NAMES = {
    0xFF0000: 'RED',   0x00FF00: 'GREEN',  0x0000FF: 'BLUE',
    0xFFFF00: 'YELLOW', 0x00FFFF: 'CYAN',   0xFF00FF: 'PURPLE',
    0xFFFFFF: 'WHITE',  0xFF8000: 'ORANGE', 0xFF0080: 'PINK',
}


# ── 函数包装器 ──────────────────────────────────

class _ScriptRecorder:
    """拦截 API 函数调用，按 uavid 记录参数签名"""

    def __init__(self):
        self._commands = {}       # uavid -> [(func_name, bound_args_dict), ...]
        self._global_events = []  # [(func_name, bound_args_dict), ...]
        self._originals = {}      # (module, name) -> original_function
        self._used_uavids = set()

    # ── 记录 ──

    def record(self, uavid, func_name, bound_args):
        self._used_uavids.add(uavid)
        if uavid not in self._commands:
            self._commands[uavid] = []
        self._commands[uavid].append((func_name, dict(bound_args)))

    def record_global(self, func_name, bound_args):
        self._global_events.append((func_name, dict(bound_args)))

    def get_commands(self, uavid):
        return self._commands.get(uavid, [])

    @property
    def uavids(self):
        return sorted(self._used_uavids)

    # ── 猴子补丁 ──

    def _make_wrapper(self, original, func_name):
        """创建一个包装器: 记录调用 → 执行原始函数"""
        recorder = self

        @functools.wraps(original)
        def wrapper(*args, **kwargs):
            # 判断是否有 Flight 对象作为第一个参数
            if args:
                flight = args[0]
                uavid = getattr(flight, 'uavid', None)
                if uavid is not None:
                    # 绑定参数签名
                    try:
                        sig = inspect.signature(original)
                        bound = sig.bind(*args, **kwargs)
                        bound.apply_defaults()
                        recorder.record(uavid, func_name, bound.arguments)
                    except Exception:
                        pass
            return original(*args, **kwargs)
        return wrapper

    def _make_delay_wrapper(self):
        """Delay 的包装器 — 记录但不分 drone"""
        recorder = self

        @functools.wraps(_Delay)
        def wrapper(ms):
            recorder.record_global('Delay', {'ms': ms})
            return _Delay(ms)
        return wrapper

    def patch(self):
        """猴子补丁 API 函数，使 exec() 中调用自动被记录"""
        import fwfii
        import fwfii.fc.basic as basic_mod
        import fwfii.led.lamp as lamp_mod
        import fwfii.utils as utils_mod

        self._originals = {}
        self._wrapped_delay = None

        # Patch fc.basic functions
        for name in _FC_BASIC_FUNCTIONS:
            if hasattr(basic_mod, name):
                orig = getattr(basic_mod, name)
                self._originals[(basic_mod, name)] = orig
                setattr(basic_mod, name, self._make_wrapper(orig, name))

        # Patch led.lamp functions
        for name in _LAMP_FUNCTIONS:
            if hasattr(lamp_mod, name):
                orig = getattr(lamp_mod, name)
                self._originals[(lamp_mod, name)] = orig
                setattr(lamp_mod, name, self._make_wrapper(orig, name))

        # Update fwfii top-level references (for "from fwfii import X")
        for name in _FC_BASIC_FUNCTIONS + _LAMP_FUNCTIONS:
            if hasattr(fwfii, name):
                orig = getattr(fwfii, name)
                if (fwfii, name) not in self._originals:
                    self._originals[(fwfii, name)] = orig
                # Replace with wrapped version from source module
                if hasattr(basic_mod, name):
                    setattr(fwfii, name, getattr(basic_mod, name))
                elif hasattr(lamp_mod, name):
                    setattr(fwfii, name, getattr(lamp_mod, name))

        # Patch Delay
        if hasattr(utils_mod, 'Delay'):
            orig_delay = getattr(utils_mod, 'Delay')
            self._originals[(utils_mod, 'Delay')] = orig_delay
            self._wrapped_delay = self._make_delay_wrapper()
            setattr(utils_mod, 'Delay', self._wrapped_delay)
            if hasattr(fwfii, 'Delay'):
                self._originals[(fwfii, 'Delay')] = getattr(fwfii, 'Delay')
                setattr(fwfii, 'Delay', self._wrapped_delay)

        return self

    def unpatch(self):
        """恢复原始函数"""
        for (mod, name), original in self._originals.items():
            try:
                setattr(mod, name, original)
            except Exception:
                pass
        self._originals.clear()
        return self


# ── .ls 文件解析 ─────────────────────────────────

def _read_ls_timestamps(ls_path):
    """从 .ls 文件中读取所有 wifiPack 的 ts (毫秒)

    返回: [ts_ms, ...] — 按写入顺序排列 (不含 dummy 头部)
    """
    timestamps = []
    try:
        with open(ls_path, 'rb') as f:
            data = f.read()
    except Exception:
        return timestamps

    # 每个 wifiPack 为 32 字节
    # struct: id(B) crc(B) ts(I LE) reg+group+rw(H) payload(24s)
    WIFIPACK_SIZE = 32
    fmt = '<BB I H 24s'

    offset = 0
    first = True
    while offset + WIFIPACK_SIZE <= len(data):
        chunk = data[offset:offset + WIFIPACK_SIZE]
        try:
            _id, _crc, ts, _reg_rw, _payload = struct.unpack(fmt, chunk)
        except struct.error:
            break

        if first:
            # 第一个是 dummy header (reg=0, ts=0) → 跳过
            first = False
        else:
            timestamps.append(ts)

        offset += WIFIPACK_SIZE

    return timestamps


# 每个 LED API 调用产生 3 个 wifiPack (LED + DUTY + LED)
_MULTI_PACK_FUNCTIONS = {
    'AllOn', 'AllOff', 'AllBlink', 'AllBreath',
    'BodyOn', 'BodyOff', 'BodyBlink', 'BodyBreath',
    'MotorOn', 'MotorOff', 'MotorBlink', 'MotorBreath',
    'MotorHorse',
}
_LED_PACK_COUNT = 3  # _lamp_op 内部: LED() + DUTY() + LED()


# ── 函数签名缓存 ─────────────────────────────────

def _get_func_defaults(func_name):
    """获取函数的参数默认值字典. 用于判断哪些参数可省略."""
    import fwfii.fc.basic as basic_mod
    import fwfii.led.lamp as lamp_mod

    for mod in [basic_mod, lamp_mod]:
        if hasattr(mod, func_name):
            func = getattr(mod, func_name)
            try:
                sig = inspect.signature(func)
                defaults = {}
                for pname, param in sig.parameters.items():
                    if param.default is not param.empty:
                        defaults[pname] = param.default
                return defaults
            except Exception:
                pass
    return {}


# ── .py 脚本生成 ─────────────────────────────────

def _format_arg(value):
    """将 Python 值格式化为源码表示"""
    if isinstance(value, bool):
        return str(value)
    elif isinstance(value, str):
        return repr(value)
    elif isinstance(value, int):
        # 颜色常量优化: 0xff0000 → RED
        if value in _COLOR_NAMES:
            return _COLOR_NAMES[value]
        return str(value)
    elif isinstance(value, float):
        return repr(value)
    elif isinstance(value, (list, tuple)):
        parts = [_format_arg(v) for v in value]
        if isinstance(value, tuple):
            return '(' + ', '.join(parts) + ')'
        else:
            return '[' + ', '.join(parts) + ']'
    else:
        return repr(value)


def _generate_script(uavid, commands, ts_list, output_path):
    """根据记录的命令 + 解析的时间戳生成 .py 脚本

    所有命令使用显式 ts (不含 Delay)
    """
    if not commands:
        return

    # 将时间戳与命令匹配 (需考虑 LED 函数产生 2 个 wifiPack)
    ts_indices = []
    pack_idx = 0
    for func_name, _ in commands:
        ts_indices.append(pack_idx)
        n_packs = _LED_PACK_COUNT if func_name in _MULTI_PACK_FUNCTIONS else 1
        pack_idx += n_packs

    resolved_ts = []
    for idx in ts_indices:
        if idx < len(ts_list):
            resolved_ts.append(ts_list[idx])
        else:
            resolved_ts.append(0)

    lines = []
    lines.append('# -*- coding: utf-8 -*-')
    lines.append('# Auto-generated drone script for UAVID=%d' % uavid)
    lines.append('# Generated by fwfii.offline_multi.MultiPlan')
    lines.append('')
    lines.append('from fwfii import Flight')
    lines.append('from fwfii import (')
    lines.append('    Arm, Disarm, Takeoff, Land, Stop,')
    lines.append('    Move2, MoveDelta,')
    lines.append('    Forward, Backward, Left, Right, Up, Down, Hover,')
    lines.append('    Yaw, Yaw2, Flip, Nod,')
    lines.append('    MaxVelXY, MaxVelZ, MaxAccXY, MaxAccZ, MaxAngularRate,')
    lines.append('    ProgrammingMode, PlanningMode,')
    lines.append('    MissionStart, MissionContinue, MissionPause,')
    lines.append('    MotorPWM, MotorsPWM,')
    lines.append(')')
    lines.append('from fwfii import (')
    lines.append('    AllOn, AllOff, AllBlink, AllBreath,')
    lines.append('    BodyOn, BodyOff, BodyBlink, BodyBreath,')
    lines.append('    MotorOn, MotorOff, MotorBlink, MotorBreath, MotorHorse,')
    lines.append(')')
    lines.append('from fwfii import (')
    lines.append('    RED, GREEN, BLUE, YELLOW, CYAN, PURPLE, WHITE, ORANGE, PINK,')
    lines.append(')')
    lines.append('')
    lines.append('f1 = Flight(%d)' % uavid)
    lines.append('')

    # 生成每条命令
    for i, (func_name, bound_args) in enumerate(commands):
        ts = resolved_ts[i]
        defaults = _get_func_defaults(func_name)

        # 收集位置参数 (非 flight, 非默认值) 和 ts
        positional = []
        ts_str = 'ts=%d' % ts

        for pname in list(bound_args.keys()):
            if pname == 'flight':
                continue
            if pname == 'ts':
                continue  # ts 单独处理, 放最后

            val = bound_args[pname]

            # 跳过 emergency=False (默认值)
            if pname == 'emergency':
                if val:  # 只在 True 时显示
                    positional.append('emergency=True')
                continue

            # 跳过其他具有默认值的参数 (如 brightness=1, passby=False)
            if pname in defaults and val == defaults[pname]:
                continue

            positional.append(_format_arg(val))

        # 构建: 位置参数在前, ts= 在最后
        parts = positional + [ts_str]
        line = '%s(f1, %s)' % (func_name, ', '.join(parts))
        lines.append(line)

    lines.append('')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return output_path


# ── MultiPlan ────────────────────────────────────

class MultiPlan:
    """多机离线任务编排器

    在一个 .py 中编写所有无人机的飞行脚本 (ts + Delay 可混用),
    一键生成各自独立的 .py + .ls + 项目结构。

    Parameters
    ----------
    output_dir : str
        输出目录

    Examples
    --------
    >>> mp = MultiPlan()
    >>> mp.add_drone(71101, pos=(20, 20))
    >>> mp.add_drone(71102, pos=(40, 20))
    >>> mp.set_music("bgm.mp3")
    >>> mp.build("choreography.py", "./show")
    """

    def __init__(self):
        self._drones = {}       # uavid -> {pos: (x,y), ip: str}
        self._music = None
        self._carpet = 40
        self._field_size = (600, 600, 300)

    # ── 配置 ──

    def add_drone(self, uavid, pos=(0, 0), ip=None):
        """添加一架无人机

        Parameters
        ----------
        uavid : int
            无人机 ID (如 71101)
        pos : tuple
            定位毯起始位置 (x, y) cm
        ip : str, optional
            无人机 IP 地址 (默认从 uavid 推导: 192.168.{group}.{num})
        """
        if ip is None:
            group = uavid // 1000
            num = uavid % 1000
            ip = '192.168.%d.%d' % (group, num)
        self._drones[uavid] = {'pos': pos, 'ip': ip}
        return self

    def set_music(self, music_path):
        """设置背景音乐路径"""
        self._music = music_path
        return self

    def set_carpet(self, size_cm):
        """设置定位毯尺寸 (cm): 40, 80, 360, 560"""
        self._carpet = size_cm
        return self

    def set_field(self, width, depth, height):
        """设置场地尺寸: 宽, 深, 高 (cm)"""
        self._field_size = (width, depth, height)
        return self

    # ── 构建 ──

    def build(self, script_path, output_dir='./multi_output'):
        """一键构建: 编译统一脚本 → 生成 per-drone .py + .ls + project.json

        Parameters
        ----------
        script_path : str
            统一飞行脚本 .py 路径
        output_dir : str
            输出目录

        Returns
        -------
        str
            输出目录路径
        """
        print('[MultiPlan] ===== 开始构建 =====')
        print('[MultiPlan] 统一脚本: %s' % script_path)
        print('[MultiPlan] 输出目录: %s/' % output_dir)
        print('[MultiPlan] 无人机: %d 架' % len(self._drones))

        # ── 准备输出目录 ──
        os.makedirs(output_dir, exist_ok=True)

        # 清空旧 .ls 文件
        for fname in os.listdir(output_dir):
            if fname.endswith('.ls'):
                os.remove(os.path.join(output_dir, fname))

        scripts_dir = os.path.join(output_dir, 'scripts')
        os.makedirs(scripts_dir, exist_ok=True)

        # ── Phase 1: 录制模式运行脚本 ──
        print('[MultiPlan] Phase 1: 录制 + 编译 .ls ...')

        recorder = _ScriptRecorder()
        recorder.patch()

        try:
            self._run_plan(script_path, output_dir)
        finally:
            recorder.unpatch()

        # ── Phase 2: 读取 .ls 时间戳 ──
        print('[MultiPlan] Phase 2: 解析 .ls 时间戳 ...')

        uavid_ts_map = {}
        for uavid in recorder.uavids:
            ls_path = os.path.join(output_dir, '%d.ls' % uavid)
            if os.path.exists(ls_path):
                ts_list = _read_ls_timestamps(ls_path)
                uavid_ts_map[uavid] = ts_list
                print('  UAVID=%d: %d 条命令, %d 个时间戳' %
                      (uavid, len(recorder.get_commands(uavid)), len(ts_list)))
            else:
                print('  [WARNING] UAVID=%d: 未生成 .ls 文件' % uavid)
                uavid_ts_map[uavid] = []

        # ── Phase 3: 生成 per-drone .py ──
        print('[MultiPlan] Phase 3: 生成 per-drone .py ...')

        for uavid in recorder.uavids:
            cmds = recorder.get_commands(uavid)
            ts_list = uavid_ts_map.get(uavid, [])
            py_path = os.path.join(scripts_dir, 'drone_%d.py' % uavid)
            _generate_script(uavid, cmds, ts_list, py_path)
            print('  → %s (%d 条命令)' % (py_path, len(cmds)))

        # ── Phase 4: 生成 project.json ──
        print('[MultiPlan] Phase 4: 生成 project.json ...')
        self._write_project_json(output_dir, scripts_dir, recorder.uavids)

        # ── 输出摘要 ──
        print()
        print('[MultiPlan] ===== 构建完成 =====')
        print('[MultiPlan] 输出: %s/' % os.path.abspath(output_dir))
        self._print_summary(output_dir)

        return output_dir

    def _run_plan(self, script_path, output_dir):
        """运行 plan() 编译脚本 → .ls 文件 (复用现有基础设施)"""
        from fwfii.quick import plan
        plan(script_path, output_dir)

    def _write_project_json(self, output_dir, scripts_dir, uavids):
        """生成项目元数据"""
        project = {
            'version': '1.0',
            'generator': 'fwfii.offline_multi.MultiPlan',
            'drones': [],
            'field': {
                'width': self._field_size[0],
                'depth': self._field_size[1],
                'height': self._field_size[2],
            },
            'carpet': self._carpet,
        }

        if self._music:
            project['music'] = self._music

        for uavid in sorted(uavids):
            info = self._drones.get(uavid, {})
            drone_entry = {
                'uavid': uavid,
                'ip': info.get('ip', '192.168.%d.%d' % (uavid // 1000, uavid % 1000)),
                'pos': list(info.get('pos', (0, 0))),
                'script': 'scripts/drone_%d.py' % uavid,
                'ls': '%d.ls' % uavid,
            }
            project['drones'].append(drone_entry)

        json_path = os.path.join(output_dir, 'project.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)

    def _print_summary(self, output_dir):
        """打印构建摘要"""
        for root, dirs, files in os.walk(output_dir):
            level = root.replace(output_dir, '').count(os.sep)
            indent = '  ' * level
            folder = os.path.basename(root) or os.path.basename(output_dir)
            print('%s%s/' % (indent, folder))
            subindent = '  ' * (level + 1)
            for fname in sorted(files):
                fpath = os.path.join(root, fname)
                size = os.path.getsize(fpath)
                print('%s%s  (%d bytes)' % (subindent, fname, size))

    # ── 信息 ──

    def info(self):
        """打印项目配置"""
        print('MultiPlan 项目配置:')
        print('  无人机: %d 架' % len(self._drones))
        for uavid, info in sorted(self._drones.items()):
            px, py = info['pos']
            print('    UAVID=%d  IP=%s  pos=(%d,%d)' %
                  (uavid, info['ip'], px, py))
        print('  场地: %d × %d cm  H ≤ %d cm' % self._field_size)
        print('  定位毯: %d cm' % self._carpet)
        if self._music:
            print('  音乐: %s' % self._music)
        return self

    def __repr__(self):
        return 'MultiPlan(%d drones)' % len(self._drones)
