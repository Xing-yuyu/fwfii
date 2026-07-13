"""
Fii 项目导出器 — 原生 .fii 蜂群项目文件输出
=============================================
直接生成官方 Fii 炫舞软件的 .fii 完整项目文件，无需第三方库。

用法::

    from fwfii import FiiExporter, fwfii_to_fii

    # 方式 1: 便捷函数
    fwfii_to_fii(
        scripts=["drone1.py", "drone2.py"],
        uavids=[98101, 98102],
        positions=[(20, 20), (60, 20)],
        output_dir="./my_show",
        music="music.mp3",
        device="F600",
        field=(600, 600, 300),
    )

    # 方式 2: FiiExporter 类
    fii = FiiExporter("my_show")
    fii.add_drone(98101, "drone1.py", pos=(20, 20))
    fii.add_drone(98102, "drone2.py", pos=(60, 20))
    fii.set_music("music.mp3")
    fii.build("./output")

输出结构::

    output/
    ├── my_show.fii                 # 项目清单 (XML)
    ├── 动作组/
    │   ├── checksums.xml           # 校验和
    │   ├── 动作组1/
    │   │   ├── webCodeAll.py       # 飞行脚本 (gtrfs 格式)
    │   │   └── webCodeAll.xml      # Blockly 可视化块
    │   ├── 动作组2/
    │   │   ├── webCodeAll.py
    │   │   └── webCodeAll.xml
    │   └── music.mp3               # 背景音乐
"""
from __future__ import division, absolute_import, print_function

import os
import re
import shutil
import sys as _sys
import xml.etree.ElementTree as ET


# ── 定位毯尺寸 → .fii AreaL/AreaW 映射 ──────────
# 官方炫舞软件的固定映射表 (AreaH 恒为 300)

_CARPET_MAP = {
    40:  (73,  73),
    80:  (115, 115),
    360: (400, 400),
    560: (600, 600),
}

# ── 颜色映射 ──────────────────────────────────────

# fwfii 十六进制常量 → gtrfs #rrggbb
_HEX_COLOR_MAP = {
    0xFF0000: '#ff0000',
    0x00FF00: '#00ff00',
    0x0000FF: '#0000ff',
    0xFFFF00: '#ffff00',
    0x00FFFF: '#00ffff',
    0xFF00FF: '#ff00ff',
    0xFFFFFF: '#ffffff',
    0xFF8000: '#ff8000',
    0xFF0080: '#ff0080',
}

# 颜色名 → gtrfs #rrggbb (webCodeAll.py 中使用名称常量)
_COLOR_TO_HEX = {
    'RED':    '#ff0000',
    'GREEN':  '#00ff00',
    'BLUE':   '#0000ff',
    'YELLOW': '#ffff00',
    'CYAN':   '#00ffff',
    'PURPLE': '#ff00ff',
    'WHITE':  '#ffffff',
    'ORANGE': '#ff8000',
    'PINK':   '#ff0080',
}


def _int_to_hex(color_int):
    """整数颜色 → '#rrggbb'"""
    if color_int in _HEX_COLOR_MAP:
        return _HEX_COLOR_MAP[color_int]
    return '#{:06x}'.format(color_int & 0xFFFFFF)


def _parse_fwfii_color(arg_str):
    """解析 fwfii 脚本中的颜色参数 → '#rrggbb'

    输入可能是: CYAN (名称), 0x00FFFF (十六进制).
    只转换确定是颜色的值: 颜色名称常量 或 0x 前缀的十六进制。
    不自动把普通整数转成颜色 (如 250 → #0000fa)，避免速度/时长被误转。
    """
    arg = arg_str.strip()
    # 颜色名称
    if arg.upper() in _COLOR_TO_HEX:
        return _COLOR_TO_HEX[arg.upper()]
    # 0x 开头
    if arg.startswith('0x') or arg.startswith('0X'):
        try:
            return '#{:06x}'.format(int(arg, 16) & 0xFFFFFF)
        except ValueError:
            pass
    # 不自动转换十进制整数 — 速度、时长等应保持原值
    return arg


# ── fwfii 脚本解析 ────────────────────────────────

# fwfii → gtrfs 参数映射 (函数有不同参数签名时需要转换)
# 大部分函数参数一致，少数需要调整

def _parse_fwfii_script(script_path):
    """解析 fwfii per-drone 脚本 → [(ts_ms, func_name, [args...]), ...]

    支持三种模式:
      - 上传模式 (纯 ts):    Func(f1, arg1, ts=1500)
      - 实时模式 (纯 Delay): Func(f1, arg1)  配合 Delay(ms) 推断时间戳
      - 混合模式:           部分有 ts=, 部分靠 Delay 推断

    返回的命令列表按 ts 升序排列。
    """
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # raw_items: [(kind, value, cmd_name, [args], ts_explicit), ...]
    raw_items = []

    for line in code.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('from ') or \
           line.startswith('import '):
            continue

        # ── Delay(ms) 独立调用 ──
        dm = re.match(r'^Delay\((\d+)\)', line)
        if dm:
            ms = int(dm.group(1))
            raw_items.append(('delay', ms, None, None, False))
            continue

        # ── Func(f1, ...) 或 Func(f1) 无参 ──
        m = re.match(r'(\w+)\(f\d*\s*,\s*(.+)\)', line)
        m_noarg = re.match(r'(\w+)\(f\d*\)', line) if not m else None

        if not m and not m_noarg:
            continue

        if m:
            cmd_name = m.group(1)
            args_str = m.group(2)
        else:
            cmd_name = m_noarg.group(1)
            args_str = ''

        if cmd_name in ('Flight',):
            continue

        ts = 0
        ts_explicit = False
        clean_args = []

        if args_str:
            parts = _split_args(args_str)
            for p in parts:
                p = p.strip()
                kv = p.split('=', 1)
                if len(kv) == 2 and kv[0].strip() == 'ts':
                    ts_explicit = True
                    try:
                        ts = int(kv[1].strip())
                    except ValueError:
                        clean_args.append(p)
                else:
                    clean_args.append(p)

        raw_items.append(('cmd', ts, cmd_name, clean_args, ts_explicit))

    # ── 时间戳推断 (支持混合模式) ──
    commands = []
    clock = 0  # Delay 累加时钟

    for item in raw_items:
        kind = item[0]
        if kind == 'delay':
            clock += item[1]  # item[1] = ms
        elif kind == 'cmd':
            ts_val, cmd_name, args, ts_explicit = item[1], item[2], item[3], item[4]
            if ts_explicit:
                # 显式 ts= 直接使用, 同时更新 clock (后续 Delay 从这之后累加)
                commands.append((ts_val, cmd_name, args))
                if ts_val > clock:
                    clock = ts_val
            else:
                # 无显式 ts: 使用当前 Delay 累加时钟
                commands.append((clock, cmd_name, args))

    # 按 ts 排序
    commands.sort(key=lambda x: x[0])
    return commands


def _split_args(s):
    """参数分割 — 处理 () 和 [] 嵌套"""
    parts = []
    paren_depth = 0
    bracket_depth = 0
    current = ''
    for ch in s:
        if ch == '(':
            paren_depth += 1
            current += ch
        elif ch == ')':
            paren_depth -= 1
            current += ch
        elif ch == '[':
            bracket_depth += 1
            current += ch
        elif ch == ']':
            bracket_depth -= 1
            current += ch
        elif ch == ',' and paren_depth == 0 and bracket_depth == 0:
            parts.append(current)
            current = ''
        else:
            current += ch
    if current.strip():
        parts.append(current)
    return parts


# ── webCodeAll.py 生成 ────────────────────────────

def _to_webcodeall_py(commands, uavid):
    """转换为 webCodeAll.py: 单个 inittime(00:00), 全用 Delay 隔开."""
    if not commands:
        return 'Start()\n'

    lines = ['Start()', 'inittime(00:00)']
    prev_ts = commands[0][0] if commands else 0

    for ts_ms, cmd, args in commands:
        delta = ts_ms - prev_ts
        if delta > 0:
            lines.append('  Delay(%d)' % delta)

        gtrfs_args = _convert_args_to_gtrfs(cmd, args)
        if gtrfs_args:
            lines.append('  %s(f1,%s)' % (cmd, gtrfs_args))
        else:
            lines.append('  %s(f1)' % cmd)

        prev_ts = ts_ms

    return '\n'.join(lines) + '\n'


def _convert_args_to_gtrfs(cmd_name, args):
    """将 fwfii 命令参数转换为 gtrfs webCodeAll.py 格式

    Returns:
        str — 参数字符串 (不含括号), 如 '#00ffff,1'
    """
    gtrfs_args = []

    # LED 函数的特殊处理
    _LED_COLOR_FUNCTIONS = {
        'AllOn', 'AllOff', 'AllBlink', 'AllBreath',
        'BodyOn', 'BodyOff', 'BodyBlink', 'BodyBreath',
    }

    if cmd_name in _LED_COLOR_FUNCTIONS:
        # LED 函数: 颜色 → #rrggbb, 添加亮度参数
        # 签名: AllOn(flight, color, brightness=1)
        #       AllBlink/AllBreath(flight, color, A, B, brightness=1)
        for i, a in enumerate(args):
            a = a.strip()
            if i == 0 and cmd_name not in ('AllOff', 'BodyOff'):
                # 第一个参数: 颜色
                gtrfs_args.append(_parse_fwfii_color(a))
            else:
                gtrfs_args.append(a)
        # 补全默认亮度
        # AllOn/BodyOn  = (color, brightness) → 2 args
        # AllBlink 等    = (color, A, B, brightness) → 4 args
        if cmd_name not in ('AllOff', 'BodyOff'):
            expected_min = 4 if cmd_name in ('AllBlink', 'AllBreath',
                                              'BodyBlink', 'BodyBreath') else 2
            while len(gtrfs_args) < expected_min:
                gtrfs_args.append('1')
        return ','.join(gtrfs_args)

    elif cmd_name == 'MotorOn':
        # MotorOn(f1, id, color) → MotorOn(f1,id,#rrggbb)
        for i, a in enumerate(args):
            a = a.strip()
            if i == 1:  # color
                gtrfs_args.append(_parse_fwfii_color(a))
            else:
                gtrfs_args.append(a)
        return ','.join(gtrfs_args)

    elif cmd_name == 'MotorHorse':
        # MotorHorse(f1, [RED, GREEN, BLUE], True, 800)
        # → MotorHorse(f1,[#rrggbb,...],True,800)
        for a in args:
            a = a.strip()
            # 处理颜色列表
            if a.startswith('[') and a.endswith(']'):
                inner = a[1:-1]
                colors = []
                for c in inner.split(','):
                    c = c.strip()
                    colors.append(_parse_fwfii_color(c))
                gtrfs_args.append('[' + ','.join(colors) + ']')
            elif a.upper() in _COLOR_TO_HEX:
                gtrfs_args.append(_parse_fwfii_color(a))
            else:
                gtrfs_args.append(a)
        return ','.join(gtrfs_args)

    else:
        # 飞行控制函数: 参数直接传递
        for a in args:
            a = a.strip()
            # 颜色参数转换
            if a.upper() in _COLOR_TO_HEX:
                gtrfs_args.append(_parse_fwfii_color(a))
            else:
                gtrfs_args.append(a)
        return ','.join(gtrfs_args)


# ── webCodeAll.xml 生成 ──────────────────────────

# ── 命令 → Blockly 块类型映射 ──────────────────
# 每个条目: (块类型, [(字段名, 参数索引, 默认值), ...])
# 参数索引 None 表示固定默认值

_BLOCKLY_MAP = {
    'Arm':       ('Goertek_UnLock', []),
    'Disarm':    ('Goertek_Lock', []),
    'Takeoff':   ('Goertek_TakeOff2', [('alt', 0)]),
    'Land':      ('Goertek_Land', []),
    'Stop':      ('Goertek_Stop', []),
    'Move2':     ('Goertek_MoveToCoord2', [('X', 0), ('Y', 1), ('Z', 2)]),
    'MoveDelta': ('Goertek_Move', [('X', 0), ('Y', 1), ('Z', 2)]),
    'AllOn':     ('Goertek_LEDTurnOnAllSingleColor2', [('color1', 0)]),
    'AllOff':    ('Goertek_LEDTurnOffAll2', []),
    'BodyOn':    ('Goertek_LEDTurnOnAllSingleColor2', [('color1', 0)]),
    'BodyOff':   ('Goertek_LEDTurnOffAll2', []),
    'AllBlink':  ('Goertek_LEDBlinkALL2',
                  [('color1', 0), ('bright', 3, '1'), ('dur', 1), ('delay', 2)]),
    'AllBreath': ('Goertek_LEDBreathALL2',
                  [('dur', 1), ('color1', 0), ('bright', 3, '1'), ('delay', 2)]),
    'BodyBlink': ('Goertek_LEDBlinkALL2',
                  [('color1', 0), ('bright', 3, '1'), ('dur', 1), ('delay', 2)]),
    'BodyBreath':('Goertek_LEDBreathALL2',
                  [('dur', 1), ('color1', 0), ('bright', 3, '1'), ('delay', 2)]),
    'MaxVelXY':  ('Goertek_HorizontalSpeed', [('VH', 0)]),
    'MaxAccXY':  ('__skip__', []),   # 合并到 _HorizSpeed
    'MaxVelZ':   ('Goertek_VerticalSpeed', [('VV', 0)]),
    'MaxAccZ':   ('__skip__', []),   # 合并到 _VertSpeed
    '_HorizSpeed': ('Goertek_HorizontalSpeed', [('VH', 0), ('AH', 1)]),
    '_VertSpeed':  ('Goertek_VerticalSpeed', [('VV', 0), ('AV', 1)]),
    'MotorOn':   ('Goertek_LEDTurnOnAllSingleColor2', [('color1', 1)]),
    'MotorOff':  ('Goertek_LEDTurnOffAll2', []),
    'MotorHorse':('Goertek_LEDHorseALL4', []),
}


def _merge_velocity_pairs(cmds):
    """预处理: 合并同一 inittime 组内的 MaxVelXY+MaxAccXY 和 MaxVelZ+MaxAccZ.

    扫描整个命令列表，将分散的速度/加速度命令配对为组合块。
    返回新的命令列表。
    """
    n = len(cmds)
    merged = [True] * n  # True = 此命令已被合并/处理, 跳过
    result = []

    for i in range(n):
        if not merged[i]:
            continue
        ts_ms, cmd_name, args = cmds[i]

        # MaxVelXY: 寻找同一组内最近的 MaxAccXY
        if cmd_name == 'MaxVelXY':
            acc_idx = None
            for j in range(i + 1, n):
                if merged[j] and cmds[j][1] == 'MaxAccXY':
                    acc_idx = j
                    break
            if acc_idx is not None:
                vh = str(args[0]).strip() if args else '0'
                ah = str(cmds[acc_idx][2][0]).strip() if cmds[acc_idx][2] else '0'
                result.append((ts_ms, '_HorizSpeed', [vh, ah]))
                merged[i] = True
                merged[acc_idx] = False  # 标记已合并
            else:
                result.append((ts_ms, cmd_name, args))
            continue

        # MaxVelZ: 寻找同一组内最近的 MaxAccZ
        if cmd_name == 'MaxVelZ':
            acc_idx = None
            for j in range(i + 1, n):
                if merged[j] and cmds[j][1] == 'MaxAccZ':
                    acc_idx = j
                    break
            if acc_idx is not None:
                vv = str(args[0]).strip() if args else '0'
                av = str(cmds[acc_idx][2][0]).strip() if cmds[acc_idx][2] else '0'
                result.append((ts_ms, '_VertSpeed', [vv, av]))
                merged[i] = True
                merged[acc_idx] = False
            else:
                result.append((ts_ms, cmd_name, args))
            continue

        # MaxAccXY / MaxAccZ 如果没被前面的配对消耗, 单独生成
        if cmd_name in ('MaxAccXY', 'MaxAccZ'):
            # 如果没被配对, 单独生成 (极少数情况)
            if cmd_name == 'MaxAccXY':
                result.append((ts_ms, '_HorizSpeed', ['0', str(args[0]) if args else '0']))
            else:
                result.append((ts_ms, '_VertSpeed', ['0', str(args[0]) if args else '0']))
            continue

        result.append((ts_ms, cmd_name, args))

    return result


def _gen_block_xml(block_type, fields, indent=12):
    """生成单个 Blockly 块的 XML 片段.
    返回 XML 行列表 (不含外层缩进).
    """
    lines = []
    pre = ' ' * indent
    lines.append('%s<block type="%s">' % (pre, block_type))
    for fname, fvalue in fields:
        lines.append('%s  <field name="%s">%s</field>' % (pre, fname, fvalue))
    lines.append('%s</block>' % pre)
    return lines


def _build_block_chain(block_xml_list):
    """将多个块嵌套串联: 每个块的 <next> 包含下一块, 形成链.

    Blockly 要求: <block A><next><block B><next><block C/></next></block></next></block>
    """
    if not block_xml_list:
        return []
    if len(block_xml_list) == 1:
        return block_xml_list[0]

    # 从右往左构建嵌套链, 不缩进 (避免深层嵌套时缩进爆炸)
    result = block_xml_list[-1]
    for i in range(len(block_xml_list) - 2, -1, -1):
        blk = block_xml_list[i]
        insert_at = len(blk) - 1
        blk.insert(insert_at, '<next>')
        for line in result:
            insert_at += 1
            blk.insert(insert_at, line)
        insert_at += 1
        blk.insert(insert_at, '</next>')
        result = blk
    return result


def _cmd_to_block_xml(ts_ms, cmd_name, args):
    """将单条命令转换为 Blockly XML 块列表.
    返回块行列表.
    """
    if cmd_name in ('__merged__', '__skip__'):
        return None

    # 查找映射
    if cmd_name not in _BLOCKLY_MAP:
        return None

    block_type, field_specs = _BLOCKLY_MAP[cmd_name]
    if block_type == '__skip__':
        return None

    # 构建字段
    fields = []
    for spec in field_specs:
        fname = spec[0]
        arg_idx = spec[1]
        default = spec[2] if len(spec) > 2 else ''

        if arg_idx is not None and arg_idx < len(args):
            val = str(args[arg_idx]).strip()
            if fname == 'color1':
                val = _parse_fwfii_color(val)
            fields.append((fname, val))
        else:
            fields.append((fname, str(default)))

    return _gen_block_xml(block_type, fields)


def _to_webcodeall_xml(commands):
    """生成完整的 webCodeAll.xml (Blockly 可视化编程块)

    根据解析出的命令列表生成对应的 Blockly XML 树，
    使官方 app 和 pyfii 可以正确加载可视化编程界面。
    """
    if not commands:
        return '''<xml xmlns="http://www.w3.org/1999/xhtml">
  <variables></variables>
  <block type="Goertek_Start" x="100" y="20"></block>
</xml>'''

    # 合并速度对, 全部放在一个 inittime(00:00) 下
    all_cmds = _merge_velocity_pairs(list(commands))

    # 构建命令链, 间隙插入 block_delay
    cmd_blocks = []
    prev_ts = commands[0][0] if commands else 0
    for ts_ms, cmd_name, args in all_cmds:
        delta = ts_ms - prev_ts
        if delta > 0:
            cmd_blocks.append(_gen_block_xml('block_delay',
                [('delay', '0'), ('time', str(delta))]))
        blk = _cmd_to_block_xml(ts_ms, cmd_name, args)
        if blk:
            cmd_blocks.append(blk)
        else:
            # 未知/跳过的命令 — 记录日志便于调试
            print('[FiiExporter] 跳过未知块: %s (ts=%d)' % (cmd_name, ts_ms),
                  file=_sys.stderr)
        prev_ts = ts_ms  # 无论块是否生成都要更新时钟

    chained = _build_block_chain(cmd_blocks) if cmd_blocks else \
        _gen_block_xml('block_delay', [('delay', '0'), ('time', '0')])

    # 包装为一个 inittime(00:00) 块
    xml_lines = []
    xml_lines.append('<xml xmlns="http://www.w3.org/1999/xhtml">')
    xml_lines.append('  <variables></variables>')
    xml_lines.append('  <block type="Goertek_Start" x="0" y="0">')
    xml_lines.append('    <next>')
    xml_lines.append('      <block type="block_inittime">')
    xml_lines.append('        <field name="time">00:00</field>')
    xml_lines.append('        <field name="color">#cccccc</field>')
    xml_lines.append('        <statement name="functionIntit">')
    for line in chained:
        xml_lines.append('          ' + line)
    xml_lines.append('        </statement>')
    xml_lines.append('      </block>')
    xml_lines.append('    </next>')
    xml_lines.append('  </block>')
    xml_lines.append('</xml>')

    return '\n'.join(xml_lines) + '\n'


# ── .fii 清单 XML 生成 ────────────────────────────

def _build_fii_xml(project_name, drones, carpet_size, music_name=None, device="F600"):
    """生成 .fii 项目清单 XML

    Parameters
    ----------
    project_name : str
        项目名称
    drones : list of dict
        [{'uavid': 98101, 'pos': (20, 20), 'group_num': 1, 'drone_num': 1}, ...]
    carpet_size : int
        定位毯尺寸 cm (40/80/360/560)
    music_name : str or None
        音乐文件名 (不含扩展名)
    device : str
        "F600" 或 "F400"
    """
    area_l, area_w = _CARPET_MAP.get(carpet_size, (600, 600))

    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<GoertekGraphicXml>')

    # 设备类型
    lines.append('  <DeviceType DeviceType="%s" />' % device)

    # 动作组声明
    for d in drones:
        lines.append('  <Actions actionname="动作组%d" />' % d['group_num'])

    # 场地尺寸 (官方固定映射, AreaH 恒为 300)
    lines.append('  <AreaL AreaL="%d" />' % area_l)
    lines.append('  <AreaW AreaW="%d" />' % area_w)
    lines.append('  <AreaH AreaH="300" />')

    # 无人机定义 (ActionFlight)
    for d in drones:
        gn = d['group_num']
        dn = d['drone_num']
        lines.append('  <ActionFlight actionfname="动作组%d无人机%d" />' % (gn, dn))
        lines.append('  <ActionFlightID actionfid="动作组%d无人机%dUAVID%d" />' %
                     (gn, dn, d['uavid']))
        lines.append('  <ActionFlightPosX actionfX="动作组%d无人机%dpos%d" />' %
                     (gn, dn, d['pos'][0]))
        lines.append('  <ActionFlightPosY actionfY="动作组%d无人机%dpos%d" />' %
                     (gn, dn, d['pos'][1]))
        lines.append('  <ActionFlightPosZ actionfZ="动作组%d无人机%dpos0" />' %
                     (gn, dn))

    # 控制时间线 (所有动作组从 time=0 开始)
    for d in drones:
        lines.append('  <动作组%dControls time="0" />' % d['group_num'])

    # 音乐
    if music_name:
        # 去掉扩展名
        name_no_ext = os.path.splitext(music_name)[0]
        lines.append('  <MusicName path="%s" />' % name_no_ext)

    lines.append('</GoertekGraphicXml>')
    return '\n'.join(lines) + '\n'


# ── checksums.xml 生成 ────────────────────────────

def _build_checksums_xml(drones):
    """生成 checksums.xml"""
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<CheckSumXml>')
    for d in drones:
        gn = d['group_num']
        dn = d['drone_num']
        lines.append('  <CheckSums flightchecksum="动作组%d无人机%dUAVID%dCheckSum0" />' %
                     (gn, dn, d['uavid']))
    lines.append('</CheckSumXml>')
    return '\n'.join(lines) + '\n'


# ═══════════════════════════════════════════════════════════════
# FiiExporter 类
# ═══════════════════════════════════════════════════════════════

class FiiExporter:
    """Fii 蜂群项目导出器

    将 fwfii per-drone 飞行脚本导出为官方 Fii 炫舞软件的 .fii 项目文件。

    Parameters
    ----------
    project_name : str
        项目名称 (也是 .fii 文件名)
    device : str
        "F600" 或 "F400"

    Examples
    --------
    >>> fii = FiiExporter("my_show")
    >>> fii.add_drone(98101, "drone_98101.py", pos=(20, 20))
    >>> fii.add_drone(98102, "drone_98102.py", pos=(60, 20))
    >>> fii.set_music("music.mp3")
    >>> fii.build("./output")
    """

    def __init__(self, project_name, device="F600"):
        self.project_name = project_name
        self.device = device
        self.drones = []       # [(uavid, script_path, pos_x, pos_y), ...]
        self.music_path = None
        self._carpet_size = 560  # 定位毯尺寸 cm (40/80/360/560)

    # ── 配置 ──────────────────────────────────────

    def add_drone(self, uavid, script_path, pos=(0, 0)):
        """添加一架无人机到项目

        Parameters
        ----------
        uavid : int
            无人机 ID
        script_path : str
            fwfii per-drone 飞行脚本路径 (含 explicit ts)
        pos : tuple
            起飞位置 (x, y) cm
        """
        self.drones.append((uavid, script_path, pos[0], pos[1]))
        return self

    def set_music(self, music_path):
        """设置背景音乐"""
        self.music_path = music_path
        return self

    def set_carpet(self, size_cm):
        """设置定位毯尺寸.

        Parameters
        ----------
        size_cm : int
            40, 80, 360, 560

        映射到 .fii AreaL/AreaW (官方固定值):
          40→73, 80→115, 360→400, 560→600
          AreaH 恒为 300
        """
        if size_cm not in _CARPET_MAP:
            raise ValueError('carpet 必须是 %s，收到 %d' %
                             (list(_CARPET_MAP.keys()), size_cm))
        self._carpet_size = size_cm
        return self

    # 保留旧名兼容
    def set_field(self, width_cm, depth_cm, height_cm):
        """(兼容) 设置场地尺寸 — 请改用 set_carpet()"""
        # 从 width 反推最接近的毯子尺寸
        closest = min(_CARPET_MAP.keys(),
                      key=lambda k: abs(_CARPET_MAP[k][0] - width_cm))
        self._carpet_size = closest
        return self

    # ── 构建 ──────────────────────────────────────

    def build(self, output_dir):
        """生成完整 .fii 项目

        Parameters
        ----------
        output_dir : str
            输出目录

        Returns
        -------
        str
            输出目录路径
        """
        if not self.drones:
            raise ValueError("至少需要添加一架无人机")

        os.makedirs(output_dir, exist_ok=True)

        # 无人机数据结构
        drone_data = []
        for i, (uavid, script_path, px, py) in enumerate(self.drones):
            group_num = i + 1  # 动作组编号从 1 开始
            drone_num = i + 1  # 无人机编号
            drone_data.append({
                'uavid': uavid,
                'script_path': script_path,
                'pos': (px, py),
                'group_num': group_num,
                'drone_num': drone_num,
            })

        # ── 动作组目录 ──
        actions_dir = os.path.join(output_dir, '动作组')
        os.makedirs(actions_dir, exist_ok=True)

        # ── 生成每个无人机的 webCodeAll.py + webCodeAll.xml ──
        for d in drone_data:
            ag_dir = os.path.join(actions_dir, '动作组%d' % d['group_num'])
            os.makedirs(ag_dir, exist_ok=True)

            # 解析 fwfii 脚本 → webCodeAll.py
            commands = _parse_fwfii_script(d['script_path'])
            py_code = _to_webcodeall_py(commands, d['uavid'])

            py_path = os.path.join(ag_dir, 'webCodeAll.py')
            with open(py_path, 'w', encoding='utf-8') as f:
                f.write(py_code)

            # webCodeAll.xml (完整 Blockly XML 树)
            xml_path = os.path.join(ag_dir, 'webCodeAll.xml')
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(_to_webcodeall_xml(commands))

            print('[FiiExporter] 动作组%d → UAVID=%d (%d 条命令)' %
                  (d['group_num'], d['uavid'], len(commands)))

        # ── checksums.xml ──
        checksums_path = os.path.join(actions_dir, 'checksums.xml')
        with open(checksums_path, 'w', encoding='utf-8') as f:
            f.write(_build_checksums_xml(drone_data))

        # ── 复制音乐 ──
        music_name = None
        if self.music_path and os.path.exists(self.music_path):
            music_name = os.path.basename(self.music_path)
            dst_music = os.path.join(actions_dir, music_name)
            shutil.copy2(self.music_path, dst_music)
            print('[FiiExporter] 音乐: %s' % music_name)

        # ── .fii 清单 ──
        fii_path = os.path.join(output_dir, self.project_name + '.fii')
        with open(fii_path, 'w', encoding='utf-8') as f:
            f.write(_build_fii_xml(self.project_name, drone_data,
                                   self._carpet_size, music_name, self.device))

        print('[FiiExporter] .fii 项目已生成: %s/' % os.path.abspath(output_dir))
        self._print_summary(output_dir)

        return output_dir

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

    # ── 读取 .fii 项目 ─────────────────────────────

    @staticmethod
    def load(project_dir):
        """从 .fii 项目目录读取配置

        解析 .fii XML 清单，提取无人机 ID、位置、场地等信息。

        Parameters
        ----------
        project_dir : str
            .fii 项目目录路径

        Returns
        -------
        dict
            {
                'project_name': str,
                'device': 'F600' | 'F400',
                'field': (width, depth, height),
                'music': str or None,
                'drones': [
                    {
                        'uavid': int,
                        'pos': (x, y),
                        'action_group': int,
                        'action_name': str,
                        'webcodeall_py': str (path),
                        'webcodeall_xml': str (path),
                    },
                    ...
                ],
            }
        """
        # 查找 .fii 文件
        fii_files = [f for f in os.listdir(project_dir) if f.endswith('.fii')]
        if not fii_files:
            raise ValueError("目录中未找到 .fii 文件: %s" % project_dir)

        fii_path = os.path.join(project_dir, fii_files[0])
        project_name = os.path.splitext(fii_files[0])[0]

        tree = ET.parse(fii_path)
        root = tree.getroot()

        # 设备类型
        device_el = root.find('DeviceType')
        device = device_el.get('DeviceType', 'F600') if device_el is not None else 'F600'

        # 场地尺寸 (从 XML 属性中提取)
        # 场地尺寸 — 从 AreaL/AreaW 反推毯子尺寸
        area_l = 600
        for el in root:
            if el.tag == 'AreaL':
                area_l = int(el.get('AreaL', 600))
                break
        # 反向查找毯子尺寸
        carpet_size = 560
        for cs, (al, _) in _CARPET_MAP.items():
            if al == area_l:
                carpet_size = cs
                break
        field = (area_l, area_l, 300)

        # 音乐
        music_el = root.find('MusicName')
        music = music_el.get('path') if music_el is not None else None

        # 无人机映射
        # 模式: ActionFlightID → 提取 UAVID
        #       ActionFlightPosX/Y → 提取位置
        drones = []
        action_groups = {}

        for el in root.findall('Actions'):
            name = el.get('actionname', '')
            if name.startswith('动作组'):
                try:
                    group_num = int(name[3:])
                    action_groups[group_num] = {'name': name}
                except ValueError:
                    pass

        # 解析 ActionFlight ID → uavid
        uavid_map = {}  # actionfname → uavid
        pos_map = {}    # actionfname → (x, y)

        for el in root.findall('ActionFlightID'):
            fid = el.get('actionfid', '')
            # 从 "动作组1无人机1UAVID98101" 提取 UAVID
            m = re.search(r'UAVID(\d+)', fid)
            if m:
                uavid = int(m.group(1))
                # 提取 actionfname 前缀
                prefix = fid[:fid.index('UAVID')]
                uavid_map[prefix] = uavid

        for el in root.findall('ActionFlightPosX'):
            fx = el.get('actionfX', '')
            m = re.search(r'(.*)pos(\d+)', fx)
            if m:
                prefix = m.group(1)
                x = int(m.group(2))
                if prefix not in pos_map:
                    pos_map[prefix] = [0, 0]
                pos_map[prefix][0] = x

        for el in root.findall('ActionFlightPosY'):
            fy = el.get('actionfY', '')
            m = re.search(r'(.*)pos(\d+)', fy)
            if m:
                prefix = m.group(1)
                y = int(m.group(2))
                if prefix not in pos_map:
                    pos_map[prefix] = [0, 0]
                pos_map[prefix][1] = y

        # 合并数据
        drones = []
        for prefix, uavid in sorted(uavid_map.items()):
            pos = pos_map.get(prefix, (0, 0))
            # 提取动作组编号
            m = re.search(r'动作组(\d+)', prefix)
            ag_num = int(m.group(1)) if m else 0

            # webCodeAll.py 路径
            ag_dir = os.path.join(project_dir, '动作组', '动作组%d' % ag_num)
            drone_data = {
                'uavid': uavid,
                'pos': (pos[0], pos[1]) if isinstance(pos, list) else pos,
                'action_group': ag_num,
                'action_name': '动作组%d' % ag_num,
                'webcodeall_py': os.path.join(ag_dir, 'webCodeAll.py'),
                'webcodeall_xml': os.path.join(ag_dir, 'webCodeAll.xml'),
            }
            drones.append(drone_data)

        return {
            'project_name': project_name,
            'device': device,
            'field': field,
            'music': music,
            'drones': drones,
        }

    # ── 信息 ──────────────────────────────────────

    def info(self):
        """打印项目配置"""
        print('FiiExporter 项目配置:')
        print('  项目名称: %s' % self.project_name)
        print('  设备: %s' % self.device)
        area_l, area_w = _CARPET_MAP.get(self._carpet_size, (600, 600))
        print('  定位毯: %d cm → Area %d×%d  H=300' %
              (self._carpet_size, area_l, area_w))
        print('  无人机: %d 架' % len(self.drones))
        for uavid, script_path, px, py in self.drones:
            print('    UAVID=%d  pos=(%d,%d)  ← %s' %
                  (uavid, px, py, os.path.basename(script_path)))
        if self.music_path:
            print('  音乐: %s' % self.music_path)
        return self

    def __repr__(self):
        return 'FiiExporter(%s, %d drones)' % (self.project_name, len(self.drones))


# ═══════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════

def fwfii_to_fii(scripts, uavids, positions, output_dir,
                 project_name=None, music=None, device="F600",
                 carpet=560):
    """便捷函数: 将 fwfii 脚本列表直接导出为 .fii 项目

    Parameters
    ----------
    scripts : list
        飞行脚本路径列表 (每个无人机一个)
    uavids : list
        无人机 ID 列表 (与 scripts 一一对应)
    positions : list
        起始位置列表 [(x, y), ...]
    output_dir : str
        输出目录
    project_name : str, optional
        项目名称 (默认取 output_dir 的 basename)
    music : str, optional
        背景音乐路径
    device : str
        "F400" 或 "F600"
    carpet : int
        定位毯尺寸 cm: 40, 80, 360, 560
        (.fii 映射: 40→73, 80→115, 360→400, 560→600; AreaH 恒=300)

    Returns
    -------
    str
        输出目录路径
    """
    n = len(scripts)
    if not (n == len(uavids) == len(positions)):
        raise ValueError('scripts/uavids/positions 长度必须一致')

    if project_name is None:
        project_name = os.path.basename(output_dir.rstrip('/\\'))

    fii = FiiExporter(project_name, device=device)
    fii.set_carpet(carpet)

    for i in range(n):
        fii.add_drone(uavids[i], scripts[i], pos=positions[i])

    if music:
        fii.set_music(music)

    return fii.build(output_dir)
