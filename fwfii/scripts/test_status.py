from fwfii.fc import *

ids = [1106, 1112, 1113]

HeartBeat.Show(True)
for id in ids:
    Flight(id)

while True:
    pass    