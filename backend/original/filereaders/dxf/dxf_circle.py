
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_entity
import dxf_constants
import math

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

    def rasterize(self, tolerance):
        path = []

        cx = self.centerPoint.getX()
        cy = self.centerPoint.getY()
        r  = self.radius

        self.addArc(path, cx-r, cy, r, r, 0, 0, 0, cx, cy+r, tolerance**2)
        self.addArc(path, cx, cy+r, r, r, 0, 0, 0, cx+r, cy, tolerance**2)
        self.addArc(path, cx+r, cy, r, r, 0, 0, 0, cx, cy-r, tolerance**2)
        self.addArc(path, cx, cy-r, r, r, 0, 0, 0, cx-r, cy, tolerance**2)

        return path


    def addArc(self, path, x1, y1, rx, ry, phi, large_arc, sweep, x2, y2, tolerance2):
        # Implemented based on the SVG implementation notes
        # plus some recursive sugar for incrementally refining the
        # arc resolution until the requested tolerance is met.
        # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        cp = math.cos(phi)
        sp = math.sin(phi)
        dx = 0.5 * (x1 - x2)
        dy = 0.5 * (y1 - y2)
        x_ = cp * dx + sp * dy
        y_ = -sp * dx + cp * dy
        r2 = ((rx*ry)**2-(rx*y_)**2-(ry*x_)**2) / ((rx*y_)**2+(ry*x_)**2)
        if r2 < 0:
            r2 = 0
        r = math.sqrt(r2)
        if large_arc == sweep:
            r = -r
        cx_ = r*rx*y_ / ry
        cy_ = -r*ry*x_ / rx
        cx = cp*cx_ - sp*cy_ + 0.5*(x1 + x2)
        cy = sp*cx_ + cp*cy_ + 0.5*(y1 + y2)

        def _angle(u, v):
            a = math.acos((u[0]*v[0] + u[1]*v[1]) /
                            math.sqrt(((u[0])**2 + (u[1])**2) *
                            ((v[0])**2 + (v[1])**2)))
            sgn = -1
            if u[0]*v[1] > u[1]*v[0]:
                sgn = 1
            return sgn * a

        psi = _angle([1,0], [(x_-cx_)/rx, (y_-cy_)/ry])
        delta = _angle([(x_-cx_)/rx, (y_-cy_)/ry], [(-x_-cx_)/rx, (-y_-cy_)/ry])
        if sweep and delta < 0:
            delta += math.pi * 2
        if not sweep and delta > 0:
            delta -= math.pi * 2

        def _getVertex(pct):
            theta = psi + delta * pct
            ct = math.cos(theta)
            st = math.sin(theta)
            return [cp*rx*ct-sp*ry*st+cx, sp*rx*ct+cp*ry*st+cy]

        # let the recursive fun begin
        def _recursiveArc(t1, t2, c1, c5, level, tolerance2):
            def _vertexDistanceSquared(v1, v2):
                return (v2[0]-v1[0])**2 + (v2[1]-v1[1])**2

            def _vertexMiddle(v1, v2):
                return [ (v2[0]+v1[0])/2.0, (v2[1]+v1[1])/2.0 ]

            if level > 18:
                # protect from deep recursion cases
                # max 2**18 = 262144 segments
                return

            tRange = t2-t1
            tHalf = t1 + 0.5*tRange
            c2 = _getVertex(t1 + 0.25*tRange)
            c3 = _getVertex(tHalf)
            c4 = _getVertex(t1 + 0.75*tRange)
            if _vertexDistanceSquared(c2, _vertexMiddle(c1,c3)) > tolerance2:
                _recursiveArc(t1, tHalf, c1, c3, level+1, tolerance2)
            path.append(c3)
            if _vertexDistanceSquared(c4, _vertexMiddle(c3,c5)) > tolerance2:
                _recursiveArc(tHalf, t2, c3, c5, level+1, tolerance2)

        t1Init = 0.0
        t2Init = 1.0
        c1Init = _getVertex(t1Init)
        c5Init = _getVertex(t2Init)
        path.append(c1Init)
        _recursiveArc(t1Init, t2Init, c1Init, c5Init, 0, tolerance2)
        path.append(c5Init)