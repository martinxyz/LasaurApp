
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_table_handler


# Viewport configuration (VPORT) table
class DXFViewportHandler(dxf_table_handler.DXFTableHandler):

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFViewportHandler, self).__init__(DXFConstants.TABLE_TYPE_VIEWPORT)

    def parseGroup(self, groupCode, value):
        pass
