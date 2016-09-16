
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_entity
import dxf_constants


class DXFLwpolyline(dxf_entity.DXFEntity):

    def __init__(self):
        super(DXFLwpolyline, self).__init__()
        self.vertices = []
        self.constantWidth = 0.0
        self.elevation = 0.0
        self.thickness = 0.0

    def getType(self):
        return dxf_constants.DXFConstants.ENTITY_TYPE_LWPOLYLINE

    def addVertex(self, vertex):
        self.vertices.append(vertex)

    def setConstantWidth(self, constantWidth):
        self.constantWidth = constantWidth

    def setElevation(self, elevation):
        self.elevation = elevation

    def setThickness(self, thickness):
        self.thickness = thickness

    def rasterize(self, tolerance):
        path = []
        tmp = None
        first = True
        for vertex in self.vertices:
            if first:
                first = False
                tmp = vertex
            else:
                path.extend([[tmp.getX(), tmp.getY()], [vertex.getX(), vertex.getY()]])
                tmp = vertex

        return path
