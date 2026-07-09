"""
fwfii → pyfii 视频桥接
======================
将 fwfii 编排的蜂群飞行导出为 pyfii 项目, 用 pyfii 生成 3D 模拟视频。

用法::

    from fwfii.pyfii_bridge import fwfii_to_fii, fwfii_show

    # 导出为 .fii 项目
    fwfii_to_fii(
        scripts=["drone1.py", "drone2.py"],
        uavids=[95101, 95102],
        positions=[(280, 280), (220, 220)],
        output_dir="./my_show",
        music="music.mp3",
        device="F600",
        field=6,
    )

    # 直接生成视频
    fwfii_show(
        scripts=["drone1.py", "drone2.py"],
        uavids=[95101, 95102],
        positions=[(280, 280), (220, 220)],
        music="music.mp3",
        output="my_show_video",
        device="F600",
        field=6,
    )
"""
from __future__ import division, absolute_import, print_function

import os
import re
import sys


# ── pyfii 路径 ──────────────────────────────────

_PYFII_PATHS = [
    "E:/Tangled",
    os.path.expanduser("~/Tangled"),
]

def _ensure_pyfii():
    """确保 pyfii 在 sys.path 中"""
    for p in _PYFII_PATHS:
        if os.path.isdir(p) and p not in sys.path:
            sys.path.insert(0, p)
    try:
        import pyfii
        return pyfii
    except ImportError:
        raise ImportError(
            "找不到 pyfii 模块。请将 pyfii 目录添加到 sys.path，"
            "或设置环境变量 PYFII_PATH"
        )


# ── fwfii 命令 → pyfii Drone 方法映射 ───────────

def _parse_script(script_path):
    """解析 fwfii/gtrfs 脚本, 提取命令列表

    Returns:
        [(timestamp_ms, cmd_name, args), ...]
    """
    with open(script_path, 'r', encoding='utf-8') as f:
        code = f.read()

    commands = []

    # 匹配模式: FuncName(f1, arg1, arg2, ..., ts=TIMESTAMP)
    # 或: FuncName(f1, arg1, arg2, ...)
    pattern = r'(\w+)\(f\d*\s*,\s*([^)]+)\)'

    for m in re.finditer(pattern, code):
        cmd = m.group(1)
        args_str = m.group(2)

        # 跳过 import / from 行
        if cmd in ('import', 'from', 'Flight', 'Delay'):
            continue

        # 解析参数
        parts = _split_args(args_str)
        ts = 0
        clean_args = []

        for p in parts:
            kv = p.strip().split('=')
            if len(kv) == 2 and kv[0].strip() == 'ts':
                try:
                    ts = int(kv[1].strip())
                except ValueError:
                    pass
            else:
                clean_args.append(p.strip())

        commands.append((ts, cmd, clean_args))

    commands.sort(key=lambda x: x[0])
    return commands


def _split_args(s):
    """简单参数分割 (处理括号嵌套)"""
    parts = []
    depth = 0
    current = ''
    for ch in s:
        if ch == '(':
            depth += 1
            current += ch
        elif ch == ')':
            depth -= 1
            current += ch
        elif ch == ',' and depth == 0:
            parts.append(current)
            current = ''
        else:
            current += ch
    if current.strip():
        parts.append(current)
    return parts


def _parse_color(arg):
    """解析颜色参数: 0xff0000 → '#ff0000'"""
    arg = arg.strip()
    if arg.startswith('0x'):
        return '#' + arg[2:].lower()
    return arg


def _parse_number(arg):
    """解析数字参数"""
    try:
        return int(arg)
    except ValueError:
        try:
            return float(arg)
        except ValueError:
            return arg


# ── 导出 .fii ───────────────────────────────────

def fwfii_to_fii(scripts, uavids, positions, output_dir,
                 music=None, device="F600", field=6):
    """将 fwfii 脚本导出为 pyfii .fii 项目

    Parameters:
        scripts:   飞行脚本路径列表 (每架无人机一个)
        uavids:    无人机 ID 列表 (与 scripts 一一对应)
        positions: 起始位置列表 [(x, y), ...]
        output_dir: 输出目录
        music:     背景音乐路径 (可选)
        device:    "F400" 或 "F600"
        field:     定位毯尺寸 (米), 6=600cm
    """
    pyfii = _ensure_pyfii()
    n = len(scripts)
    assert n == len(uavids) == len(positions), "scripts/uavids/positions 长度必须一致"

    DroneClass = pyfii.Drone6 if device == "F600" else pyfii.Drone
    config = pyfii.drone_config_6m if device == "F600" else pyfii.drone_config_4m

    drones = []
    for i in range(n):
        uavid = uavids[i]
        px, py = positions[i]
        group = uavid // 1000
        num = uavid % 1000
        ip = f"192.168.{group}.{num}"

        d = DroneClass(px, py, config, ip)
        drones.append(d)

        # 解析脚本并调用 pyfii 方法
        commands = _parse_script(scripts[i])
        last_intime = -1  # 跟踪上次 intime 的时间

        for ts_ms, cmd, args in commands:
            t_sec = int(ts_ms / 1000.0)

            try:
                # ── 时间轴 ──
                def _set_time(t):
                    nonlocal last_intime
                    t_int = int(t)
                    if t_int > last_intime:
                        d.intime(t_int)
                        last_intime = t_int

                if cmd == 'Arm':
                    pass
                elif cmd == 'Takeoff':
                    alt = int(_parse_number(args[0])) if args else 80
                    d.takeoff(max(t_sec, 1), alt)
                elif cmd == 'Land':
                    _set_time(t_sec)
                    d.land()
                elif cmd == 'Move2':
                    x = int(_parse_number(args[0]))
                    y = int(_parse_number(args[1]))
                    z = int(_parse_number(args[2]))
                    _set_time(t_sec)
                    d.move2(x, y, z)
                elif cmd == 'MoveDelta':
                    dx = int(_parse_number(args[0]))
                    dy = int(_parse_number(args[1]))
                    dz = int(_parse_number(args[2]))
                    _set_time(t_sec)
                    d.move(dx, dy, dz)
                elif cmd == 'AllOn':
                    color = _parse_color(str(args[0]))
                    if device == "F600":
                        d.AllOn(color, timestamp=int(ts_ms))
                    else:
                        d.TurnOnAll(color, timestamp=int(ts_ms))
                elif cmd == 'AllOff':
                    if device == "F600":
                        d.AllOff(timestamp=int(ts_ms))
                    else:
                        d.TurnOffAll(timestamp=int(ts_ms))
                elif cmd == 'AllBlink':
                    color = _parse_color(str(args[0]))
                    if device == "F600":
                        d.AllOn(color, timestamp=int(ts_ms))
                    else:
                        d.BlinkFastAll([color], timestamp=int(ts_ms))
                elif cmd == 'AllBreath':
                    color = _parse_color(str(args[0]))
                    if device == "F600":
                        d.AllOn(color, timestamp=int(ts_ms))
                    else:
                        d.Breath(color, timestamp=int(ts_ms))
                elif cmd == 'MaxVelXY':
                    _set_time(t_sec)
                    d.VelXY(int(_parse_number(args[0])), 200)
                elif cmd == 'MaxVelZ':
                    _set_time(t_sec)
                    d.VelZ(int(_parse_number(args[0])), 200)
                elif cmd == 'MaxAccXY':
                    _set_time(t_sec)
                    d.AccXY(int(_parse_number(args[0])))
                elif cmd == 'MaxAccZ':
                    _set_time(t_sec)
                    d.AccZ(int(_parse_number(args[0])))
                elif cmd == 'Disarm':
                    pass
                elif cmd in ('Delay', 'SetFlightMode', 'ProgrammingMode',
                            'PlanningMode', 'MissionStart', 'GenLsEnd'):
                    pass
            except Exception as e:
                pass  # 跳过不兼容的指令 (如坐标超出 pyfii 范围)

    # Finalize
    for d in drones:
        d.end()

    # 复制音乐到动作组目录
    music_name = None
    if music and os.path.exists(music):
        music_name = os.path.basename(music)
        target_music = os.path.join(output_dir, "动作组", music_name)
        os.makedirs(os.path.dirname(target_music), exist_ok=True)
        import shutil
        shutil.copy2(music, target_music)

    # 保存 .fii
    project_name = os.path.basename(output_dir.rstrip('/\\'))
    fii = pyfii.Fii(os.path.join(output_dir, project_name), drones,
                    music=f"动作组/{music_name}" if music_name else '')
    fii.save(infii=False, addlights=False, field=field)

    print(f"[pyfii_bridge] .fii 项目已生成: {output_dir}/")
    return output_dir


# ── 生成视频 ────────────────────────────────────

def fwfii_show(scripts, uavids, positions, output="preview",
               music=None, device="F600", field=6, fps=60):
    """从 fwfii 脚本直接生成 3D 模拟视频

    Parameters:
        scripts:   飞行脚本路径列表
        uavids:    无人机 ID 列表
        positions: 起始位置 [(x, y), ...]
        output:    输出文件名 (不含扩展名)
        music:     背景音乐
        device:    "F400" / "F600"
        field:     定位毯尺寸 (米)
        fps:       视频帧率
    """
    pyfii = _ensure_pyfii()

    # 先导出 .fii
    tmp_dir = output + "_fii_tmp"
    fwfii_to_fii(scripts, uavids, positions, tmp_dir,
                 music=music, device=device, field=field)

    # 读取 .fii
    print(f"[pyfii_bridge] 读取 .fii → 计算轨迹...")
    data, t0, music_info, field_size, device_type = pyfii.read_fii(
        tmp_dir, getfield=True, fps=fps, ignore_acc=False, getdevice=True
    )

    # 渲染视频
    print(f"[pyfii_bridge] 渲染视频 → {output}.mp4 ...")
    pyfii.show(data, t0, music_info, device=device_type, field=field_size,
               save=output, FPS=fps, max_fps=fps, skin=1)

    # 也生成 3D 版
    pyfii.show(data, t0, music_info, device=device_type, field=field_size,
               save=output + '_3D', ThreeD=True,
               imshow=[90, 3], d=(600, 500),
               FPS=fps, max_fps=fps, skin=1)

    print(f"[pyfii_bridge] 视频生成完成!")
    print(f"  2D: {output}.mp4")
    print(f"  3D: {output}_3D.mp4")

    # 清理临时文件
    import shutil
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    return [f"{output}.mp4", f"{output}_3D.mp4"]


# ── 从 SwarmProject 导出 ────────────────────────

def swarm_to_video(swarm_project, output="swarm_preview", fps=60):
    """从 SwarmProject 直接生成视频"""
    scripts = [s for _, s, _, _ in swarm_project.drones]
    uavids = [u for u, _, _, _ in swarm_project.drones]
    positions = [(px, py) for _, _, px, py in swarm_project.drones]

    return fwfii_show(
        scripts=scripts,
        uavids=uavids,
        positions=positions,
        output=output,
        music=swarm_project.music_file,
        device="F600" if swarm_project.field_size[0] >= 500 else "F400",
        field=swarm_project.field_size[0] // 100,
        fps=fps,
    )
