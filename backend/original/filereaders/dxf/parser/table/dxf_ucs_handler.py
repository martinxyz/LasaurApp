
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_table_handler


# User Coordinate System (UCS) table
class DXFUcsHandler(dxf_table_handler.DXFTableHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFUcsHandler, self).__init__(DXFConstants.TABLE_TYPE_UCS)

    def parseGroup(self, groupCode, value):
        pass
