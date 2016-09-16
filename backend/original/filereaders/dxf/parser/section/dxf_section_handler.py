
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import filereaders.dxf.parser.dxf_handler

class DXFSectionHandler(filereaders.dxf.parser.dxf_handler.DXFHandler):

    def __init__(self, name):
        super(DXFSectionHandler, self).__init__(name)

    def startSection(self):
        pass

    def endSection(self):
        pass


