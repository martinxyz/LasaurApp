
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.entities import dxf_entity_handler
from filereaders.dxf.dxf_spline import DXFSpline
from filereaders.dxf.util.spline_point import SplinePoint


class DXFSplineHandler(dxf_entity_handler.DXFEntityHandler):

    GROUP_CODE_CONTROL_POINT_X                  = 10
    GROUP_CODE_CONTROL_POINT_Y                  = 20
    GROUP_CODE_CONTROL_POINT_Z                  = 30
    GROUP_CODE_FIT_POINT_X                      = 11
    GROUP_CODE_FIT_POINT_Y                      = 21
    GROUP_CODE_FIT_POINT_Z                      = 31
    GROUP_CODE_START_TANGENT_X                  = 12
    GROUP_CODE_START_TANGENT_Y                  = 22
    GROUP_CODE_START_TANGENT_Z                  = 32
    GROUP_CODE_END_TANGENT_X                    = 13
    GROUP_CODE_END_TANGENT_Y                    = 23
    GROUP_CODE_END_TANGENT_Z                    = 33
    GROUP_CODE_FIT_TOLERANCE                    = 44
    GROUP_CODE_KNOTS                            = 40
    GROUP_CODE_WEIGHTS                          = 41
    GROUP_CODE_CONTROL_POINT_TOLERANCE          = 42
    GROUP_CODE_KNOT_TOLERANCE                   = 43
    GROUP_CODE_NUMBER_OF_FIT_POINTS             = 74
    GROUP_CODE_NUMBER_OF_CONTROL_POINTS         = 73
    GROUP_CODE_NUMBER_OF_CONTROL_POINTS2        = 96
    GROUP_CODE_NUMBER_OF_NODES                  = 72
    GROUP_CODE_NUMBER_OF_NODES2                 = 95
    GROUP_CODE_DEGREE                           = 71

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFSplineHandler, self).__init__(DXFConstants.ENTITY_TYPE_SPLINE)

        self.spline             = None
        self.splinePoint        = None


    def getEntity(self):
        return self.spline

    def startEntity(self):
        super(DXFSplineHandler, self).startEntity()
        self.spline = DXFSpline()

    def parseGroup(self, groupCode, value):

        if groupCode == self.GROUP_CODE_DEGREE:
            self.spline.setDegree(value.getInt())

        elif groupCode == self.GROUP_CODE_NUMBER_OF_CONTROL_POINTS or \
             groupCode == self.GROUP_CODE_NUMBER_OF_CONTROL_POINTS2:

            self.spline.setControlPointsSize(value.getInt())

        elif groupCode == self.GROUP_CODE_NUMBER_OF_FIT_POINTS:
            self.spline.setFitPointsSize(value.getInt())

        elif groupCode == self.GROUP_CODE_NUMBER_OF_NODES or \
             groupCode == self.GROUP_CODE_NUMBER_OF_NODES2:

            self.spline.setKnotsSize(value.getInt())

        elif groupCode == self.GROUP_CODE_FIT_TOLERANCE:
            self.spline.setFitTolerance(value.getDouble())

        elif groupCode == self.GROUP_CODE_KNOTS:
            self.spline.addKnot(value.getDouble())

        elif groupCode == self.GROUP_CODE_KNOT_TOLERANCE:
            self.spline.setKnotsTolerance(value.getDouble())

        elif groupCode == self.GROUP_CODE_WEIGHTS:
            self.spline.addWeight(value.getDouble())

        elif groupCode == self.GROUP_CODE_CONTROL_POINT_TOLERANCE:
            self.spline.setControlPointTolerance(value.getDouble())

        elif groupCode == self.GROUP_CODE_FIT_POINT_X:
            self.splinePoint = SplinePoint()
            self.splinePoint.setType(SplinePoint.TYPE_FIT_POINT)
            self.splinePoint.setX(value.getDouble())
            self.spline.addFitPoint(self.splinePoint)

        elif groupCode == self.GROUP_CODE_FIT_POINT_Y:
            self.splinePoint.setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_FIT_POINT_Z:
            self.splinePoint.setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_CONTROL_POINT_X:
            self.splinePoint = SplinePoint()
            self.splinePoint.setType(SplinePoint.TYPE_CONTROL_POINT)
            self.splinePoint.setX(value.getDouble())
            self.spline.addControlPoint(self.splinePoint)

        elif groupCode == self.GROUP_CODE_CONTROL_POINT_Y:
            self.splinePoint.setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_CONTROL_POINT_Z:
            self.splinePoint.setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_TANGENT_X:
            self.splinePoint = SplinePoint()
            self.splinePoint.setType(SplinePoint.TYPE_START_TANGENT)
            self.splinePoint.setX(value.getDouble())
            self.spline.addStartTangent(self.splinePoint)

        elif groupCode == self.GROUP_CODE_START_TANGENT_Y:
            self.splinePoint.setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_START_TANGENT_Z:
            self.splinePoint.setZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_END_TANGENT_X:
            self.splinePoint = SplinePoint()
            self.splinePoint.setType(SplinePoint.TYPE_END_TANGENT)
            self.splinePoint.setX(value.getDouble())
            self.spline.addEndTangent(self.splinePoint)

        elif groupCode == self.GROUP_CODE_END_TANGENT_Y:
            self.splinePoint.setY(value.getDouble())

        elif groupCode == self.GROUP_CODE_END_TANGENT_Z:
            self.splinePoint.setZ(value.getDouble())

        else:
            self.parseCommonProperty(groupCode, value, self.spline)
