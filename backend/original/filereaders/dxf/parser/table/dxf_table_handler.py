
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import filereaders.dxf.parser.dxf_handler


# Table
class DXFTableHandler(filereaders.dxf.parser.dxf_handler.DXFHandler):

    def __init__(self, name):
        super(DXFTableHandler, self).__init__(name)

    def startTable(self):
        pass

    def endTable(self):
        self.parseIt = False

    def startRow(self):
        pass

    def endRow(self):
        pass

    def parseGroup(self, groupCode, value):
        pass

