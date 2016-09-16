
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.entities import dxf_entity_handler
from filereaders.dxf.dxf_arc import DXFArc


class DXFArcHandler(dxf_entity_handler.DXFEntityHandler):

    GROUP_CODE_RADIUS                           = 40
    GROUP_CODE_ANGLE_START                      = 50
    GROUP_CODE_ANGLE_END                        = 51
    GROUP_CODE_COUNTERCLOCKWISE                 = 73

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFArcHandler, self).__init__(DXFConstants.ENTITY_TYPE_ARC)

        self.arc = None

    def getEntity(self):
        return self.arc

    def startEntity(self):
        super(DXFArcHandler, self).startEntity()
        self.arc = DXFArc()

    def parseGroup(self, groupCode, value):
        if groupCode == self.GROUP_CODE_START_X:
            self.arc.getCenterPoint().setX(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Y:
            self.arc.getCenterPoint().setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Z:
            self.arc.getCenterPoint().setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_RADIUS:
            self.arc.setRadius(value.getDouble())

        elif groupCode == self.GROUP_CODE_ANGLE_START:
            self.arc.setAngleStart(value.getDouble())

        elif groupCode == self.GROUP_CODE_ANGLE_END:
            self.arc.setAngleEnd(value.getDouble())

        elif groupCode == self.GROUP_CODE_COUNTERCLOCKWISE:
            self.arc.setCounterclockwise(value.getDouble())

        else:
            self.parseCommonProperty(groupCode, value, self.arc)

