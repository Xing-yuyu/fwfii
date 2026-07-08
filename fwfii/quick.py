"""
fwfii 快捷操作模块
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight
from fwfii.utils import Delay
from fwfii.planning.deliver import scriptsGenerator, scriptsTransferOverSock
from fwfii.atom import AtomRepo
import time
import os

_connections = {}

# ==========================================
# 心跳连接
# ==========================================

def connect(uavid):
    """连接无人机，启动心跳"""
    if uavid in _connections:
        disconnect(uavid)

    d = TcpDelivery(vo=None)
    h = HeartBeat()
    time.sleep(3)
    f1 = Flight(uavid)
    _connections[uavid] = (d, h, f1)
    print(f"[fwfii] 已连接 {uavid}")
    return d, h, f1


def disconnect(uavid=None):
    """断开连接。不传参数则断开所有"""
    if uavid is None:
        for uid in list(_connections.keys()):
            _disconnect_one(uid)
    else:
        _disconnect_one(uavid)


def _disconnect_one(uavid):
    if uavid in _connections:
        d, h, f1 = _connections[uavid]
        h.close()
        d.close()
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
    """上传 .ls 到无人机"""
    if ip is None:
        group = uavid // 1000
        num = uavid % 1000
        ip = f"192.168.{group}.{num}"

    print(f"[fwfii] 上传到 {ip}...")
    s = scriptsTransferOverSock(path, ip)
    s.start()
    s.join()
    print(f"[fwfii] 上传完成")


def mission_start(segments, countdown=5):
    """同步起飞倒计时"""
    from fwfii.fc import DelayLaunch

    print(f"倒计时 {countdown} 秒...")
    for t in range(countdown * 1000, 0, -100):
        for seg in segments:
            DelayLaunch(seg, t)
        Delay(100)
    print("发射！")