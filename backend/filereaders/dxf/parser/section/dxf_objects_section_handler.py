
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_section_handler


class DXFObjectsSectionHandler(dxf_section_handler.DXFSectionHandler):

    def __init__(self, name):
        super(DXFObjectsSectionHandler, self).__init__(name)

    def parseGroup(self, groupCode, value):
        pass
