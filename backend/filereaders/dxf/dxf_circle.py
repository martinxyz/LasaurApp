
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_entity
import dxf_constants

from filereaders.dxf.util.point import Point


class DXFCircle(dxf_entity.DXFEntity):

    def __init__(self):
        super(DXFCircle, self).__init__()

        self.centerPoint = Point()
        self.radius = 0.0

    def getType(self):
        return dxf_constants.DXFConstants.ENTITY_TYPE_CIRCLE

    def getCenterPoint(self):
        return self.centerPoint;

    def getRadius(self):
        return self.radius

    def setRadius(self, radius):
        self.radius = radius

    def __repr__(self):
        return "centerPoint = [ " + str(self.centerPoint.getX()) + ", " + str(self.centerPoint.getY()) + ", " + str(self.centerPoint.getZ()) + " ], radius = " + str(self.radius)
