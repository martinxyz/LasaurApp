
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.entities import dxf_entity_handler
from filereaders.dxf.dxf_circle import DXFCircle


class DXFCircleHandler(dxf_entity_handler.DXFEntityHandler):

    GROUP_CODE_RADIUS                           = 40

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFCircleHandler, self).__init__(DXFConstants.ENTITY_TYPE_CIRCLE)

        self.circle = None

    def getEntity(self):
        return self.circle

    def startEntity(self):
        super(DXFCircleHandler, self).startEntity()
        self.circle = DXFCircle()

    def parseGroup(self, groupCode, value):
        if groupCode == self.GROUP_CODE_START_X:
            self.circle.getCenterPoint().setX(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Y:
            self.circle.getCenterPoint().setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Z:
            self.circle.getCenterPoint().setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_RADIUS:
            self.circle.setRadius(value.getDouble())

        else:
            self.parseCommonProperty(groupCode, value, self.circle)


