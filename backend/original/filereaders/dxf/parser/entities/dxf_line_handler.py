
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.entities import dxf_entity_handler
from filereaders.dxf.dxf_line import DXFLine


class DXFLineHandler(dxf_entity_handler.DXFEntityHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFLineHandler, self).__init__(DXFConstants.ENTITY_TYPE_LINE)

        self.line = None

    def getEntity(self):
        return self.line

    def startEntity(self):
        super(DXFLineHandler, self).startEntity()
        self.line = DXFLine()

    def parseGroup(self, groupCode, value):
        if groupCode == self.GROUP_CODE_START_X:
            self.line.getStartPoint().setX(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Y:
            self.line.getStartPoint().setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Z:
            self.line.getStartPoint().setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_END_X:
            self.line.getEndPoint().setX(value.getDouble())

        elif groupCode == self.GROUP_CODE_END_Y:
            self.line.getEndPoint().setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_END_Z:
            self.line.getEndPoint().setZ(value.getDouble())

        else:
            self.parseCommonProperty(groupCode, value, self.line)
