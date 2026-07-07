from fwfii.fc import *

f1 = Flight(1001)

AddMark('a', 1, 2, 3)

Move2Marker(f1, 'a')

nod(f1, 'x', 30)

SimpleHarmonic(f1, 'x', 1, 2, 3, 1, 90, 3, 1)

CylindricalSpiral(f1, 'x', 'a', 1, 90, 1, 1)

MovewHeading(f1, 'x', 1, True, 30)