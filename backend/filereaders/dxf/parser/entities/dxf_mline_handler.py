
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.entities import dxf_entity_handler


class DXFLineHandler(dxf_entity_handler.DXFEntityHandler):

    GROUP_CODE_LINE_STYLENAME                   = 2
    GROUP_CODE_LINE_STYLE_ID                    = 340
    GROUP_CODE_LINE_SCALE_FACTOR                = 40
    GROUP_CODE_LINE_JUSTIFICATION               = 70
    GROUP_CODE_LINE_FLAGS                       = 71
    GROUP_CODE_LINE_NUMBER_OF_VERTICES          = 72
    GROUP_CODE_LINE_NUMBER_OF_LINESTYLEELEMENTS = 73
    GROUP_CODE_LINE_VERTEX_X                    = 11
    GROUP_CODE_LINE_VERTEX_Y                    = 21
    GROUP_CODE_LINE_VERTEX_Z                    = 31
    GROUP_CODE_LINE_DIRECTION_X                 = 12
    GROUP_CODE_LINE_DIRECTION_Y                 = 22
    GROUP_CODE_LINE_DIRECTION_Z                 = 32
    GROUP_CODE_LINE_MITER_DIRECTION_X           = 13
    GROUP_CODE_LINE_MITER_DIRECTION_Y           = 23
    GROUP_CODE_LINE_MITER_DIRECTION_Z           = 33
    GROUP_CODE_LINE_ELEMENT_PARAMETER_COUNT     = 74
    GROUP_CODE_LINE_ELEMENT_PARAMETER           = 41
    GROUP_CODE_LINE_FILL_PARAMETER_COUNT        = 75
    GROUP_CODE_LINE_FILL_PARAMETER              = 42

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFLineHandler, self).__init__(DXFConstants.ENTITY_TYPE_LINE)

    def startEntity(self):
        pass

    def endEntity(self):
        pass
