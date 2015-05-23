
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_entity
import dxf_constants
import logging


log = logging.getLogger(__name__)

class DXFPolyline(dxf_entity.DXFEntity):

    def __init__(self):
        super(DXFPolyline, self).__init__()
        self.vertices = []
        self.startWidth = 0
        self.endWidth = 0

    def getType(self):
        return dxf_constants.DXFConstants.ENTITY_TYPE_POLYLINE

    def addVertex(self, vertex):
        self.vertices.append(vertex)

    def setStartWidh(self, startWidth):
        self.startWidth = startWidth

    def setEndWidth(self, endWidth):
        self.endWidth = endWidth

    def setSurfaceType(self, surfaceType):
        log.warning("no 'surfaceType' defined")

    def setRows(self, rows):
        log.warning("no 'rows' defined")

    def setColumns(self, columns):
        log.warning("no 'columns' defined")

    def setSurfaceDensityRows(self, surfaceDensityRows):
        log.warning("no 'surfaceDensityRows' defined")

    def setSurfaceDensityColumns(self, surfaceDensityColumns):
        log.warning("no 'surfaceDensityColumns' defined")

    def __repr__(self):
        return "numVertices = " + str(len(self.vertices))

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
