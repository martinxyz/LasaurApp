
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import math


class Point(object):

    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self.x = x
        self.y = y
        self.z = z

    def setX(self, x):
        self.x = x

    def getX(self):
        return self.x

    def setY(self, y):
        self.y = y

    def getY(self):
        return self.y

    def setZ(self, z):
        self.z = z

    def getZ(self):
        return self.z

    def getLength(self):
        return math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2) + math.pow(self.z, 2))

    def __repr__(self):
        return "[ " + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + " ]"
