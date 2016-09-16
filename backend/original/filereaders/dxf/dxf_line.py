
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from . import dxf_entity
from . import dxf_constants

from filereaders.dxf.util.point import Point

class DXFLine(dxf_entity.DXFEntity):

    def __init__(self):
        super(DXFLine, self).__init__()

        self.startPoint = Point()
        self.endPoint = Point()


    def getType(self):
        return dxf_constants.DXFConstants.ENTITY_TYPE_LINE

    def getStartPoint(self):
        return self.startPoint

    def getEndPoint(self):
        return self.endPoint

    def __repr__(self):
        return "startPoint = [ " + str(self.startPoint.getX()) + ", " + str(self.startPoint.getY()) + ", " + str(self.startPoint.getZ()) + \
               " ], endPoint = [ " + str(self.endPoint.getX()) + ", " + str(self.endPoint.getY()) + ", " + str(self.endPoint.getZ()) + " ]"

    def rasterize(self, tolerance):
        return [[self.startPoint.getX(), self.startPoint.getY()],
                [self.endPoint.getX(),   self.endPoint.getY()]]
