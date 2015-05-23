
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import filereaders.dxf.util.point


class Vector(filereaders.dxf.util.point.Point):

    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        super(Vector, self).__init__(x, y, z)

    def normalize(self):
        len = self.getLength()
        self.x = (self.x / len)
        self.y = (self.y / len)
        self.z = (self.z / len)
