from fwfii.fc import Flight
from fwfii.atom import AtomRepo

f1 = Flight(71101)
print(f"Flight ID: {f1.uavid}")
print(f"AtomRepo 初始: {AtomRepo.length()}")

from fwfii.fc import Arm
Arm(f1)
print(f"Arm 后: {AtomRepo.length()}")

from fwfii.fc import HeartBeatData
HeartBeatData(f1)
print(f"HeartBeat 后: {AtomRepo.length()}")