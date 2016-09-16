
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_section_handler


class DXFEntitiesSectionHandler(dxf_section_handler.DXFSectionHandler):

    GROUP_CODE_ENTITY_START         = 0         # LINE, CIRCLE, ARC, ...

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFEntitiesSectionHandler, self).__init__(DXFConstants.SECTION_TYPE_ENTITIES)

    def startSection(self):
        pass

    def endSection(self):
        if self.parseIt:
            self.handler.endEntity()

    def parseGroup(self, groupCode, value):
        if  groupCode == self.GROUP_CODE_ENTITY_START:
            if self.parseIt:
                if self.handler.hasFollowingSequence():
                    self.handler.parseGroup(groupCode, value)
                    return
                else:
                    self.handler.endEntity()
            try:
                self.handler = self.handlers[value.getString()]
                self.handler.setDocument(self.document)
                self.handler.startEntity()
                self.parseIt = True
            except KeyError:
                self.parseIt = False

        elif self.parseIt:
            self.handler.parseGroup(groupCode, value)


