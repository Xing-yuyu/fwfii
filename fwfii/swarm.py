"""
蜂群飞行模块 — 多机项目一键编译/上传/起飞/音乐
==============================================

支持:
  - 从 pyfii .fii 项目文件加载
  - 手动编程添加无人机
  - 批量编译 plan() → .ls
  - 批量上传 deliver() → WiFi
  - 同步起飞 + 倒计时
  - 背景音乐播放

用法::

    from fwfii.swarm import SwarmProject

    # 从 pyfii 项目加载
    swarm = SwarmProject("E:/F流浪地球")
    swarm.compile("./output")
    swarm.deliver()
    swarm.launch_with_music(countdown=5)

    # 手动创建
    swarm = SwarmProject()
    swarm.add_drone(71101, "drone1.py", pos=(20, 20))
    swarm.add_drone(71102, "drone2.py", pos=(40, 20))
    swarm.set_music("music.mp3")
    swarm.compile().deliver().launch_with_music()
"""
from __future__ import division, absolute_import, print_function

import os
import re
import time
import xml.etree.ElementTree as ET
from threading import Thread

from fwfii.gtrfs_compat import convert_gtrfs_script
from fwfii.quick import connect, disconnect, plan, deliver
from fwfii.fc import Flight
from fwfii.fc.advanced import DelayLaunch
from fwfii.fc.basic import Arm, PlanningMode, MissionStart
from fwfii.utils import Delay
from fwfii.utils.music import (
    load_music, play_music, stop_music,
    set_music_volume, is_music_playing,
)


class SwarmProject:
    """蜂群项目 — 管理多架无人机的完整工作流"""

    def __init__(self, project_dir=None):
        self.drones = []       # [(uavid, script_path, pos_x, pos_y), ...]
        self.music_file = None
        self.field_size = (600, 600, 300)
        self._connections = {}  # uavid → (delivery, heartbeat, flight)
        if project_dir:
            self.load(project_dir)

    # ── 配置 ──────────────────────────────────────

    def add_drone(self, uavid, script_path, pos=(0, 0)):
        """手动添加一架无人机

        Parameters:
            uavid: 无人机 ID
            script_path: 飞行脚本路径 (pyfii 或 fwfii 格式)
            pos: (x, y) 定位毯起始位置 (cm)
        """
        self.drones.append((uavid, script_path, pos[0], pos[1]))
        return self

    def set_music(self, music_path):
        """设置背景音乐文件 (.mp3 / .flac / .wav)"""
        self.music_file = music_path
        return self

    # ── pyfii .fii 加载 ────────────────────────────

    def load(self, project_dir):
        """从 .fii 项目目录加载 (官方格式)

        自动解析:
          - .fii 文件 → 无人机 ID、起始位置、音乐
          - 动作组/动作组N/webCodeAll.py → 飞行脚本 (官方格式)
          - 动作组/动作组N/offlineExcuteScript.py → 飞行脚本 (pyfii 格式, 备选)
        """
        project_dir = os.path.abspath(project_dir)

        # 找 .fii 文件
        fii_files = [f for f in os.listdir(project_dir) if f.endswith('.fii')]
        if not fii_files:
            raise FileNotFoundError(f"目录 {project_dir} 中没有找到 .fii 文件")

        fii_path = os.path.join(project_dir, fii_files[0])
        action_dir = os.path.join(project_dir, "动作组")

        # 解析 XML
        tree = ET.parse(fii_path)
        root = tree.getroot()

        # 场地尺寸
        for el in root:
            if el.tag == 'AreaL':
                self.field_size = (int(el.get('AreaL', 600)),
                                   self.field_size[1],
                                   self.field_size[2])
            elif el.tag == 'AreaW':
                self.field_size = (self.field_size[0],
                                   int(el.get('AreaW', 600)),
                                   self.field_size[2])
            elif el.tag == 'AreaH':
                self.field_size = (self.field_size[0],
                                   self.field_size[1],
                                   int(el.get('AreaH', 300)))

        # 音乐
        for el in root:
            if el.tag == 'MusicName':
                music_name = el.get('path', '')
                # 在项目目录下找音乐文件
                for f in os.listdir(project_dir):
                    if music_name in f and f.split('.')[-1] in ('mp3', 'flac', 'wav', 'mp4'):
                        self.music_file = os.path.join(project_dir, f)
                        break
                # 也在动作组目录下找
                if not self.music_file:
                    for f in os.listdir(action_dir):
                        if music_name in f and f.split('.')[-1] in ('mp3', 'flac', 'wav', 'mp4'):
                            self.music_file = os.path.join(action_dir, f)
                            break

        # 解析无人机映射
        drone_map = {}  # action_group_name → {uavid, pos_x, pos_y}
        for el in root:
            tag = el.tag
            if tag == 'ActionFlightID':
                fid = el.get('actionfid', '')
                # 提取 UAVID: "动作组1无人机1UAVID95101" → 95101
                m = re.search(r'UAVID(\d+)', fid)
                if m:
                    # 解析 action group 名称
                    ag_name = fid.split('无人机')[0]  # "动作组1"
                    if ag_name not in drone_map:
                        drone_map[ag_name] = {}
                    drone_map[ag_name]['uavid'] = int(m.group(1))
            elif tag == 'ActionFlightPosX':
                fx = el.get('actionfX', '')
                m = re.search(r'pos(\d+)', fx)
                if m:
                    ag_name = fx.split('无人机')[0]
                    if ag_name not in drone_map:
                        drone_map[ag_name] = {}
                    drone_map[ag_name]['pos_x'] = int(m.group(1))
            elif tag == 'ActionFlightPosY':
                fy = el.get('actionfY', '')
                m = re.search(r'pos(\d+)', fy)
                if m:
                    ag_name = fy.split('无人机')[0]
                    if ag_name not in drone_map:
                        drone_map[ag_name] = {}
                    drone_map[ag_name]['pos_y'] = int(m.group(1))

        # 加载每个无人机的脚本
        for ag_name, info in sorted(drone_map.items()):
            if 'uavid' not in info:
                continue
            uavid = info['uavid']
            pos_x = info.get('pos_x', 0)
            pos_y = info.get('pos_y', 0)

            # 找动作组目录
            ag_num = re.search(r'(\d+)$', ag_name)
            if ag_num:
                ag_dir = os.path.join(action_dir, ag_name)
                if not os.path.isdir(ag_dir):
                    # 尝试 "动作组1" → "动作组 1" 空格变体
                    pass
                script_path = os.path.join(ag_dir, "webCodeAll.py")
                if not os.path.exists(script_path):
                    script_path = os.path.join(ag_dir, "offlineExcuteScript.py")
                if os.path.exists(script_path):
                    self.drones.append((uavid, script_path, pos_x, pos_y))

        print(f"[Swarm] 从 {project_dir} 加载了 {len(self.drones)} 架无人机")
        if self.music_file:
            print(f"[Swarm] 音乐: {os.path.basename(self.music_file)}")
        return self

    # ── 编译 ──────────────────────────────────────

    def compile(self, output_dir="./swarm_output"):
        """批量编译所有无人机脚本 → .ls 文件

        自动将 gtrfs/官方 格式转换为 fwfii 兼容格式
        """
        os.makedirs(output_dir, exist_ok=True)

        # 清理旧 .ls
        for f in os.listdir(output_dir):
            if f.endswith('.ls'):
                os.remove(os.path.join(output_dir, f))

        scripts_dir = os.path.join(output_dir, "_scripts")
        os.makedirs(scripts_dir, exist_ok=True)

        for uavid, script_path, pos_x, pos_y in self.drones:
            # 转换为 fwfii 兼容格式
            fwfii_script = os.path.join(scripts_dir,
                                        f"drone_{uavid}.py")
            convert_gtrfs_script(script_path, fwfii_script)

            # 编译
            print(f"[Swarm] 编译 UAVID={uavid}  ← {os.path.basename(script_path)}")
            plan(fwfii_script, output_dir)

        # 确认
        ls_files = [f for f in os.listdir(output_dir) if f.endswith('.ls')]
        print(f"[Swarm] 编译完成: {len(ls_files)} 个 .ls 文件 → {output_dir}/")
        for f in sorted(ls_files):
            size = os.path.getsize(os.path.join(output_dir, f))
            print(f"  {f}  ({size} bytes)")

        return self

    # ── 上传 ──────────────────────────────────────

    def deliver(self, output_dir="./swarm_output"):
        """批量上传 .ls 到所有无人机"""
        for uavid, _, _, _ in self.drones:
            group = uavid // 1000
            num = uavid % 1000
            ip = f"192.168.{group}.{num}"
            print(f"\n[Swarm] 上传 → UAVID={uavid}  ({ip})")
            deliver(uavid, output_dir, ip=ip)
        return self

    # ── 起飞 ──────────────────────────────────────

    def launch(self, countdown=5):
        """同步起飞 — 连接所有无人机, PlanningMode, 倒计时, MissionStart

        注意: 调用前需确保 .ls 已上传到无人机
        """
        n = len(self.drones)
        if n == 0:
            print("[Swarm] 没有无人机可起飞")
            return self

        print(f"\n[Swarm] 连接 {n} 架无人机...")
        flights = []
        for uavid, _, pos_x, pos_y in self.drones:
            print(f"  连接 UAVID={uavid}  pos=({pos_x},{pos_y})")
            d, h, f = connect(uavid)
            f.position = (pos_x, pos_y, 0, 0)
            self._connections[uavid] = (d, h, f)
            flights.append(f)

        # 切换到 PlanningMode
        print("[Swarm] 切换 PlanningMode ...")
        for f in flights:
            PlanningMode(f)
        Delay(500)

        # 倒计时
        print(f"\n[Swarm] 倒计时 {countdown} 秒...")
        for t in range(countdown, 0, -1):
            print(f"  {t}...")
            Delay(1000)

        # 同步启动!
        print("[Swarm] 起飞!")
        for f in flights:
            MissionStart(f)

        # 监控
        print("\n[Swarm] 监控中 (Ctrl+C 中止)...")
        try:
            while True:
                time.sleep(1)
                parts = []
                for uavid, _, _, _ in self.drones:
                    if uavid in self._connections:
                        _, _, f = self._connections[uavid]
                        x, y, z, _ = f.position
                        parts.append(f"#{uavid}:({x:.0f},{y:.0f},{z:.0f})[{f.flightmode}]")
                print("  " + " | ".join(parts))
        except KeyboardInterrupt:
            print("\n[Swarm] 监控停止 (无人机继续自主飞行)")

        return self

    def launch_with_music(self, countdown=5):
        """同步起飞 + 播放背景音乐"""
        # 加载音乐
        if self.music_file and os.path.exists(self.music_file):
            print(f"[Swarm] 加载音乐: {os.path.basename(self.music_file)}")
            load_music(self.music_file)
            set_music_volume(0.7)

        # 连接 + 起飞
        self.launch(countdown)

        # 播放
        if is_music_playing() is False and self.music_file:
            play_music(loops=0)

        return self

    # ── 停止 ──────────────────────────────────────

    def stop_music(self, fade_ms=2000):
        """停止音乐"""
        stop_music(fade_ms=fade_ms)
        return self

    def disconnect_all(self):
        """断开所有无人机连接"""
        disconnect()
        self._connections.clear()
        return self

    # ── 信息 ──────────────────────────────────────

    def info(self):
        """打印项目信息"""
        print(f"蜂群项目: {len(self.drones)} 架无人机")
        print(f"场地: {self.field_size[0]}×{self.field_size[1]}cm  H≤{self.field_size[2]}cm")
        if self.music_file:
            print(f"音乐: {os.path.basename(self.music_file)}")
        print("无人机:")
        for uavid, script, px, py in self.drones:
            group = uavid // 1000
            num = uavid % 1000
            print(f"  UAVID={uavid}  IP=192.168.{group}.{num}  "
                  f"pos=({px},{py})  script={os.path.basename(script)}")

    def __repr__(self):
        return f"SwarmProject({len(self.drones)} drones)"
