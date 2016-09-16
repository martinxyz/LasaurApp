
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_point


class DXFVertex(dxf_point.DXFPoint):

    def __init__(self):

        super(DXFVertex, self).__init__()

        self.x = 0
        self.y = 0
        self.z = 0
        self.bulge = 0.0
        self.startWidth = 0.0
        self.endWidth = 0.0

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

    def setBulge(self, bulge):
        self.bulge = bulge

    def setStartWidth(self, startWidth):
        self.startWidth = startWidth

    def setEndWidth(self, endWidth):
        self.endWidth = endWidth

    def setPolyFaceMeshVertex0(self, mesh0):
        pass

    def setPolyFaceMeshVertex1(self, mesh1):
        pass

    def setPolyFaceMeshVertex2(self, mesh2):
        pass

    def setPolyFaceMeshVertex3(self, mesh3):
        pass

    def __repr__(self):
        return "vertex = [ " + str(self.getX()) + ", " + str(self.getY()) + ", " + str(self.getZ()) + " ]"

