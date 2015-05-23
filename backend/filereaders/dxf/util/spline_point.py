
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import filereaders.dxf.util.point


class SplinePoint(filereaders.dxf.util.point.Point):

    TYPE_UNKNOW                                 = 0
    TYPE_CONTROL_POINT                          = 1
    TYPE_FIT_POINT                              = 2
    TYPE_START_TANGENT                          = 3
    TYPE_END_TANGENT                            = 4

    def __init__(self):
        self.type = self.TYPE_UNKNOW

    def isControlPoint(self):
        return self.type == self.TYPE_CONTROL_POINT

    def isFitPoint(self):
        return self.type == self.TYPE_FIT_POINT

    def isStartTangent(self):
        return self.type == self.TYPE_START_TANGENT

    def isEndTangent(self):
        return self.type == self.TYPE_END_TANGENT

    def setType(self, type):
        self.type = type

    def getType(self):
        return self.type
