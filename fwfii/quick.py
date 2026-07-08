"""
fwfii 快捷操作模块
"""
from fwfii.atom.delivery import TcpDelivery
from fwfii.fc.heartbeat import HeartBeat
from fwfii.fc import Flight
from fwfii.utils import Delay
from fwfii.planning.deliver import scriptsGenerator
from fwfii.planning.uploader import MissionUploader
import time
from pathlib import Path

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

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    s = scriptsGenerator(output_path, append=False)
    s.start()
    Delay(100)

    with Path(script_path).open(encoding='utf-8') as f:
        exec(f.read())

    GenLsEnd()
    s.stop(timeout=10)
    s.join(timeout=5)

    print(f"[fwfii] 已生成 .ls 文件到 {output_path}")
    for file in sorted(output_path.iterdir()):
        if file.is_file():
            print(f"  {file.name} ({file.stat().st_size} bytes)")


def deliver(uavid, path, ip=None):
    """上传 .ls 到无人机"""
    if ip is None:
        group = uavid // 1000
        num = uavid % 1000
        ip = f"192.168.{group}.{num}"

    print(f"[fwfii] 上传到 {ip}...")
    uploader = MissionUploader(ip)
    results = uploader.upload_path(path, uavid=uavid if Path(path).is_file() else None)
    failed = [result for result in results if not result.success]
    if failed:
        raise RuntimeError("upload failed: {}".format(failed[0].error))
    print(f"[fwfii] 上传完成")
    return results


def mission_start(segments, countdown=5):
    """同步起飞倒计时"""
    from fwfii.fc import DelayLaunch

    print(f"倒计时 {countdown} 秒...")
    for t in range(countdown * 1000, 0, -100):
        for seg in segments:
            DelayLaunch(seg, t)
        Delay(100)
    print("发射！")
