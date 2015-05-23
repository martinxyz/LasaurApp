
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_table_handler


# View (VIEW) table
class DXFViewHandler(dxf_table_handler.DXFTableHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFViewHandler, self).__init__(DXFConstants.TABLE_TYPE_VIEW)

    def parseGroup(self, groupCode, value):
        pass
