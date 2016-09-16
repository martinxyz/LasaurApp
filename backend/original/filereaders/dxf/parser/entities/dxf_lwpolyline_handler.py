
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.entities import dxf_entity_handler

from filereaders.dxf.dxf_lwpolyline import DXFLwpolyline
from filereaders.dxf.dxf_vertex import DXFVertex


class DXFLwpolylineHandler(dxf_entity_handler.DXFEntityHandler):

    GROUP_CODE_VERTEX_BULGE                     = 42
    GROUP_CODE_START_WIDTH                      = 40
    GROUP_CODE_END_WIDTH                        = 41
    GROUP_CODE_CONSTANT_WIDTH                   = 43
    GROUP_CODE_ELEVATION                        = 38
    GROUP_CODE_THICKNESS                        = 39

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFLwpolylineHandler, self).__init__(DXFConstants.ENTITY_TYPE_LWPOLYLINE)

        self.lwpolyline = None
        self.vertex = None

    def getEntity(self):
        return self.lwpolyline

    def startEntity(self):
        super(DXFLwpolylineHandler, self).startEntity()
        self.lwpolyline = DXFLwpolyline()
    
    def parseGroup(self, groupCode, value):
        if groupCode == self.GROUP_CODE_START_X:
            self.vertex = DXFVertex()
            self.lwpolyline.addVertex(self.vertex)
            self.vertex.setX(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Y:
            self.vertex.setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_Z:
            self.vertex.setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_VERTEX_BULGE:
            self.vertex.setBulge(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_WIDTH:
            self.vertex.setStartWidth(value.getDouble())

        elif groupCode == self.GROUP_CODE_END_WIDTH:
            self.vertex.setEndWidth(value.getDouble())

        elif groupCode == self.GROUP_CODE_CONSTANT_WIDTH:
            self.lwpolyline.setConstantWidth(value.getDouble())

        elif groupCode == self.GROUP_CODE_ELEVATION:
            self.lwpolyline.setElevation(value.getDouble())

        elif groupCode == self.GROUP_CODE_THICKNESS:
            self.lwpolyline.setThickness(value.getDouble())

        else:
            self.parseCommonProperty(groupCode, value, self.lwpolyline)
