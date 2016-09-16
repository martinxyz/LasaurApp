
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from . import dxf_section_handler


class DXFObjectsSectionHandler(dxf_section_handler.DXFSectionHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFObjectsSectionHandler, self).__init__(DXFConstants.SECTION_TYPE_OBJECTS)

    def parseGroup(self, groupCode, value):
        pass
