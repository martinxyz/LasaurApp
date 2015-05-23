
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.table import dxf_table_handler


# Block Record (BLOCK_RECORD) table
class DXFBlockRecordHandler(dxf_table_handler.DXFTableHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFBlockRecordHandler, self).__init__(DXFConstants.TABLE_TYPE_BLOCK_RECORD)

    def parseGroup(self, groupCode, value):
        pass
