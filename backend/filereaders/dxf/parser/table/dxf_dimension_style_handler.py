
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.table import dxf_table_handler


# Dimension Style (DIMSTYPE) table
class DXFDimensionStyleHandler(dxf_table_handler.DXFTableHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFDimensionStyleHandler, self).__init__(DXFConstants.TABLE_TYPE_DIMENSION_STYLE)

    def parseGroup(self, groupCode, value):
        pass
