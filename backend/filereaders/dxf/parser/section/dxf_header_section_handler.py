
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_section_handler
from filereaders.dxf.dxf_constants import DXFConstants


class DXFHeaderSectionHandler(dxf_section_handler.DXFSectionHandler):

    GROUP_CODE_HEADER_VARIABLE_START            = 9
    GROUP_CODE_PRIMARY_TEXT                     = 1
    GROUP_CODE_ATTRIBUTE_NAME                   = 2
    GROUP_CODE_OTHER_TEXT                       = 3
    GROUP_CODE_ENTITY_HANDLE                    = 5
    GROUP_CODE_LINE_TYPE_NAME                   = 6
    GROUP_CODE_TEXT_STYLE_NAME                  = 7
    GROUP_CODE_LAYER_NAME                       = 8
    GROUP_CODE_POINT_X                          = 10
    GROUP_CODE_POINT_Y                          = 20
    GROUP_CODE_POINT_Z                          = 30
    GROUP_CODE_DOUBLE                           = 40
    GROUP_CODE_ANGLE                            = 50
    GROUP_CODE_COLOR                            = 62
    GROUP_CODE_INTEGER                          = 70
    GROUP_CODE_INTEGER_16BIT                    = 280
    GROUP_CODE_BOOLEAN                          = 290

    def __init__(self):

        super(DXFHeaderSectionHandler, self).__init__(DXFConstants.SECTION_TYPE_HEADER)

        self.variable = None

    def startSection(self):
        pass

    def endSection(self):
        pass

    def parseGroup(self, groupCode, value):
        if  groupCode == self.GROUP_CODE_HEADER_VARIABLE_START:
            self.parseIt = True
            if value == DXFConstants.HEADER_VARIABLE_ACADVER:
                self.variable = self.document.header.version
            else:
                self.parseIt = False

        elif self.parseIt:
            if groupCode == DXFConstants.GROUP_CODE_PRIMARY_TEXT:
                self.variable.setString(value)
