from __future__ import division, absolute_import, print_function


class obstacle(object):
    def __init__(self, centroid):
        self._centroid = centroid

    @property
    def centroid(self):
        return self._centroid

    @centroid.setter
    def centroid(self, value):
        self._centroid = value


class Ball(obstacle):
    def __init__(self, centroid, radius):
        super(Ball, self).__init__(centroid)
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value


class cube(obstacle):
    Obstacles = {}

    def __init__(self, centroid, length, width, height, objtype):
        super(cube, self).__init__(centroid)
        self._length = length
        self._width = width
        self._height = height
        self._objtype = objtype
        cube.addObstacle(self)

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value):
        self._length = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

    @property
    def objtype(self):
        return self._objtype

    @objtype.setter
    def objtype(self, value):
        self._objtype = value

    @staticmethod
    def addObstacle(obj):
        cube.Obstacles[obj] = obj

    @staticmethod
    def removeObstacle(obj):
        cube.Obstacles.pop(obj, None)


'''
if __name__ == '__main__':
    o = obstacle((1, 2, 3))
    print(o.centroid)

    o.centroid = (4, 5, 6)
    print(o.centroid)

    b = Ball((1, 2, 3), 3)
    print(b.centroid, b.radius)
    b.radius = 5
    print(b.radius)

'''
