
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from . import dxf_entity
from . import dxf_constants
import math

class DXFSpline(dxf_entity.DXFEntity):

    __SPLINE_CLOSED = 0x01
    __SPLINE_PERIODIC = 0x02
    __SPLINE_RATIONAL = 0x04
    __SPLINE_PLANAR = 0x08
    __SPLINE_LINEAR = 0x10

    def __init__(self):
        super(DXFSpline, self).__init__()

        self.degree                 = 0
        self.controlPointsSize      = 0
        self.fitPointsSize          = 0
        self.knotsSize              = 0
        self.fitTolerance           = 0.0
        self.knotsTolerance         = 0.0
        self.controlPointTolerance  = 0.0
        self.knots                  = []
        self.weights                = []
        self.splinePoints           = []
        self.fitPoints              = []
        self.controlPoints          = []
        self.startTangents          = []
        self.endTangents            = []

    def getType(self):
        return dxf_constants.DXFConstants.ENTITY_TYPE_SPLINE

    def setDegree(self, degree):
        self.degree = degree

    def setControlPointsSize(self, controlPointsSize):
        self.controlPointsSize = controlPointsSize

    def setFitPointsSize(self, fitPointsSize):
        self.fitPointsSize = fitPointsSize

    def setKnotsSize(self, nodePointsSize):
        self.knotsSize = nodePointsSize

    def setFitTolerance(self, fitTolerance):
        self.fitTolerance = fitTolerance

    def setKnotsTolerance(self, knotsTolerance):
        self.knotsTolerance = knotsTolerance

    def setControlPointTolerance(self, controlPointTolerance):
        self.controlPointTolerance = controlPointTolerance

    def addKnot(self, knot):
        self.knots.append(knot)

    def addWeight(self, weight):
        self.weights.append(weight)

    def addFitPoint(self, fitPoint):
        self.splinePoints.append(fitPoint)
        self.fitPoints.append(fitPoint)

    def addControlPoint(self, controlPoint):
        self.splinePoints.append(controlPoint)
        self.controlPoints.append(controlPoint)

    def addStartTangent(self, controlPoint):
        self.splinePoints.append(controlPoint)
        self.startTangents.append(controlPoint)

    def addEndTangent(self, controlPoint):
        self.splinePoints.append(controlPoint)
        self.endTangents.append(controlPoint)

    def rasterize(self, tolerance):
        path = []
        controls = []
        for controlPoint in self.controlPoints:
            controls.append([controlPoint.getX(), controlPoint.getY(), controlPoint.getZ()])
        if not self.weights:
            self.weights = [1.0] * self.controlPointsSize

        self.addSpline(path, self.degree, controls, self.knots, self.weights, bool(self.flags & self.__SPLINE_PERIODIC), tolerance**2)
        return path

    def addSpline(self, path, degree, controls, x, weights, periodic, tolerance2):
        # Implementation originates from Kevin Loney:
        # https://github.com/Protospace/LasaurApp/blob/03809ba389f0750bb2e82cb84431c139db5852f5/backend/filereaders/dxf_reader.py
        #
        # Implementation described in "An Introduction to NURBS" by David F. Rogers
        # Google books: http://books.google.ca/books?id=MaW4XiScJ7cC&lpg=PA1&pg=PP1#v=onepage&q&f=false
        # Example source: http://www.nar-associates.com/nurbs/c_code.html

        npts = len(controls)

        order = degree + 1
        nplusc = npts + order

        def _rationalBasis(t):
            # critical path (for some files, 95% of the cpu time is spent in here)

            # calculate the first order nonrational basis functions n[i]
            temp = []
            for i in range(1, nplusc):
                temp.append(1 if ((t >= x[i - 1]) and (t < x[i])) else 0)

            # calculate the higher order nonrational basis functions
            for k in range(2, order+1):
                for i in range(0, nplusc - k):
                    # if the lower order basis function is zero skip the calculation
                    d = temp[i] * ((t-x[i]))/(x[i+k-1]-x[i]) if temp[i] != 0 else 0

                    # if the lower order basis function is zero skip the calculation
                    e = temp[i+1] * ((x[i+k]-t))/(x[i+k]-x[i+1]) if temp[i + 1] != 0 else 0

                    temp[i] = d + e

            if t == float(x[nplusc - 1]):
                temp[npts - 1] = 1

            # calculate sum for denominator of rational basis functions
            total = 0
            for i in range(0, npts):
                total += temp[i] * weights[i]

            r = []
            # normalize rational basis
            for i in range(0, npts):
                r.append((temp[i] * weights[i])/(total) if total != 0 else 0)

            return r

        def _evalPoint(t):
            p = [0.0, 0.0, 0.0]

            # Get the basis function at t
            nbasis = _rationalBasis(t)

            # Perform matrix mutiplication between basis and control points
            for j in range(0, 3):
                for i in range(0, npts):
                    p[j] += nbasis[i] * controls[i][j]

            # Only interested in the x and y coordinates
            return p[0:2]

        def _recursiveSpline(level, t1, p1, t2, p2, tolerance2):
            def _distPointSegment(p, u, v):
                # Calculate distance between a point and a segment using vector projection

                l2 = self._distance2(u, v)
                if l2 == 0.0:
                    # Zero length segment case
                    return self._distance(p, u)

                t = self._vectorDot(self._vectorSub(p, u), self._vectorSub(v, u)) / l2
                if t < 0.0:
                    # Before the start of the segment
                    return self._distance(p, u)
                if t > 1.0:
                    # After the end of the segment
                    return self._distance(p, v)

                # Distance between point and it's projection onto the segment
                return self._distance(p, [u + t * (v - u) for u,v in zip(u, v)])

            if level > 18:
                # protect from deep recursion cases
                # max 2**18 = 262144 segments
                return

            t0 = 0.5 * (t1 + t2)
            p0 = _evalPoint(t0)

            if _distPointSegment(p0, p1, p2) > tolerance2:
                _recursiveSpline(level + 1, t1, p1, t0, p0, tolerance2)

                path.append(p0[0:2])

                _recursiveSpline(level + 1, t0, p0, t2, p2, tolerance2)

        # Evaluate the NURBS curve
        t_prev = 0.0
        pt_prev = _evalPoint(t_prev)
        path.append(pt_prev)

        for i in range(1, npts):
            t_curr = x[nplusc - 1] * float(i) / (npts - 1)
            pt_curr = _evalPoint(t_curr)

            _recursiveSpline(0, t_prev, pt_prev, t_curr, pt_curr, tolerance2)

            path.append(pt_curr)

            t_prev = t_curr
            pt_prev = pt_curr

    def _vectorDot(self, u, v):
        return sum([a*b for a, b in zip(u, v)])

    def _vectorSub(self, u, v):
        return [u - v for u,v in zip(u, v)]

    def _magnitude2(self, u):
        return self._vectorDot(u, u)
    def _magnitude(self, u):
        return math.sqrt(self._vectorDot(u, u))

    def _distance2(self, u, v):
        t = self._vectorSub(u, v)
        return self._vectorDot(t, t)
    def _distance(self, u, v):
        return math.sqrt(self._distance2(u, v))


