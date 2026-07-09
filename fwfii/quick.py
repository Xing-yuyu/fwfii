"""
fwfii 快捷操作模块
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight
from fwfii.utils import Delay
from fwfii.utils.logger import start_log, stop_log, is_logging
from fwfii.utils.music import load_music, play_music, stop_music, pause_music, unpause_music, set_music_volume, is_music_playing, wait_music
from fwfii.planning.deliver import scriptsGenerator
from fwfii.atom import AtomRepo
from fwfii.fc.advanced import Transfer, End_Transfer2
from socket import socket, AF_INET, SOCK_STREAM
import struct
import time
import os
import threading

_connections = {}
_lock = threading.Lock()
_shared_delivery = None
_shared_heartbeat = None

# ==========================================
# 心跳连接
# ==========================================

def connect(uavid):
    """连接无人机，启动心跳。等待连接稳定后返回"""
    global _shared_delivery, _shared_heartbeat

    with _lock:
        if uavid in _connections:
            disconnect(uavid)

        # Share a single TcpDelivery for all drones — prevents
        # multiple senders competing for the shared AtomRepo queue
        if _shared_delivery is None:
            _shared_delivery = TcpDelivery(vo=None)
        if _shared_heartbeat is None:
            _shared_heartbeat = HeartBeat()

        d = _shared_delivery
        h = _shared_heartbeat
        time.sleep(3)
        f1 = Flight(uavid)
        _connections[uavid] = (d, h, f1)
        print(f"[fwfii] 已连接 {uavid}")

        # Wait for TCP connection + first position response (max 15s)
        group = uavid // 1000
        num = uavid % 1000
        destaddr = (f'192.168.{group}.{num}', 10014)
        waited = 0
        while waited < 15:
            # Check TCP connection established
            if destaddr in d.server and d.server[destaddr][0]:
                # Check real position arrived (z != 0)
                _, _, z, _ = f1.position
                if z != 0:
                    print(f"[fwfii] {uavid} 就绪 (z={z:.0f}cm)")
                    break
            time.sleep(0.5)
            waited += 0.5
        else:
            print(f"[fwfii] ⚠ {uavid} 连接超时，请检查无人机")

        return d, h, f1


def disconnect(uavid=None):
    """断开连接。不传参数则断开所有"""
    global _shared_delivery, _shared_heartbeat

    with _lock:
        if uavid is None:
            for uid in list(_connections.keys()):
                _disconnect_one(uid)
            if _shared_heartbeat:
                _shared_heartbeat.close()
                _shared_heartbeat = None
            if _shared_delivery:
                _shared_delivery.close()
                _shared_delivery = None
        else:
            _disconnect_one(uavid)
            if len(_connections) == 0:
                if _shared_heartbeat:
                    _shared_heartbeat.close()
                    _shared_heartbeat = None
                if _shared_delivery:
                    _shared_delivery.close()
                    _shared_delivery = None


def _disconnect_one(uavid):
    if uavid in _connections:
        d, h, f1 = _connections[uavid]
        HeartBeat.removeFlight(f1)
        del _connections[uavid]
        print(f"[fwfii] 已断开 {uavid}")


# ==========================================
# 离线模式
# ==========================================

def plan(script_path, output_path='./output'):
    """编译飞行脚本 → .ls 文件"""
    from fwfii.fc import GenLsEnd

    os.makedirs(output_path, exist_ok=True)
    s = scriptsGenerator(output_path, append=False)
    s.start()
    Delay(100)

    with open(script_path, encoding='utf-8') as f:
        exec(f.read())

    GenLsEnd()
    Delay(300)

    timeout = 10
    waited = 0
    while not s._end and waited < timeout:
        Delay(100)
        waited += 0.1

    s._running = False
    s.join(timeout=5)

    print(f"[fwfii] 已生成 .ls 文件到 {output_path}")
    for fname in os.listdir(output_path):
        fsize = os.path.getsize(os.path.join(output_path, fname))
        print(f"  {fname} ({fsize} bytes)")


def deliver(uavid, path, ip=None):
    """上传 .ls 飞行脚本到无人机

    协议 (port 10034):
        [Transfer zigbeePack (40B)] [文件数据 (512B/chunk)] [checksum (4B LE)]

    Parameters:
        uavid: 无人机 ID (group*1000+number)
        path:  .ls 文件路径或目录
        ip:    无人机 IP (可选，默认从 uavid 推导)
    """
    if ip is None:
        group = uavid // 1000
        num = uavid % 1000
        ip = f"192.168.{group}.{num}"

    # 收集要上传的文件列表
    if os.path.isdir(path):
        files = [
            os.path.join(path, f) for f in os.listdir(path)
            if f.endswith('.ls') and os.path.isfile(os.path.join(path, f))
        ]
        if not files:
            print(f"[fwfii] ⚠ 目录 {path} 中没有找到 .ls 文件")
            return
    else:
        files = [path]

    print(f"[fwfii] 上传到 {ip}:10034 ... ({len(files)} 个文件)")

    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            file_uavid = int(filename.rsplit('.', 1)[0])
        except ValueError:
            print(f"[fwfii] ⚠ 跳过 {filename}: 无法解析 uavid")
            continue

        filesize = os.path.getsize(filepath)
        flight = Flight(file_uavid)

        # ── 连接 port 10034 ──
        sock = None
        checksum = 0
        try:
            sock = socket(AF_INET, SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, 10034))

            # ── 1. 发送 Transfer 命令头 (40B zigbeePack) ──
            transfer_cmd = Transfer(flight, 1, filesize + 4, file_uavid)
            sock.sendall(bytes(transfer_cmd))
            print(f"[fwfii] → Transfer 头已发送: {filename} ({filesize} bytes)")
            Delay(200)

            # ── 2. 发送文件数据 ──
            sent = 0
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(512)
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    for b in chunk:
                        checksum = (checksum + b) & 0xFFFFFFFF
                    sent += len(chunk)
                    print(f"\r[fwfii] {filename}: {sent}/{filesize} bytes "
                          f"({sent * 100 // filesize}%)", end='')
                    Delay(40)

            # ── 3. 发送 checksum ──
            sock.sendall(struct.pack("<I", checksum))
            print(f"\n[fwfii] {filename}: 完成, checksum=0x{checksum:08x}")

        except Exception as e:
            print(f"\n[fwfii] ✗ {filename}: 传输失败 — {e}")
            continue
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    print(f"[fwfii] 上传完成")


def mission_start(segments, countdown=5):
    """同步起飞倒计时 + 启动任务"""
    from fwfii.fc import DelayLaunch

    # Send countdown sync to all segments
    print(f"倒计时 {countdown} 秒...")
    for t in range(countdown * 1000, 0, -100):
        for seg in segments:
            DelayLaunch(seg, t)
        Delay(100)
    # Final launch signal (t=0)
    for seg in segments:
        DelayLaunch(seg, 0)
    print("发射！")
