
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from . import dxf_table_handler


# Line Type (LTYPE) table
class DXFLineTypeHandler(dxf_table_handler.DXFTableHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFLineTypeHandler, self).__init__(DXFConstants.TABLE_TYPE_LINE_TYPE)

    def parseGroup(self, groupCode, value):
        pass
