
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from . import dxf_section_handler


class DXFTablesSectionHandler(dxf_section_handler.DXFSectionHandler):

    GROUP_CODE_ENTITY_START         = 0
    GROUP_CODE_NAME                 = 2
    TABLE_START                     = "TABLE"
    TABLE_END                       = "ENDTAB"

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFTablesSectionHandler, self).__init__(DXFConstants.SECTION_TYPE_TABLES)

    def parseGroup(self, groupCode, value):
        # 0: TABLE, start of the table
        if  groupCode == self.GROUP_CODE_ENTITY_START and value.getString() == self.TABLE_START:
            return

        # 0: ENDTAB, end of the table
        elif groupCode == self.GROUP_CODE_ENTITY_START and value.getString() == self.TABLE_END:
            if self.parseIt:
                if self.handler.parseIt:
                    self.handler.endRow()
                self.handler.endTable()
                self.parseIt = False

        # 2: <TYPE>, what type of table is it?
        elif not self.parseIt and groupCode == self.GROUP_CODE_NAME:

            try:
                self.handler = self.handlers[value.getString()]
                self.handler.setDocument(self.document)
                self.handler.startTable()
                self.handler.parseIt = False
                self.parseIt = True
            except KeyError:
                self.parseIt = False

        elif self.parseIt:
            # 0: <TYPE>, start of a new entry/row
            if groupCode == self.GROUP_CODE_ENTITY_START and value.getString() == self.handler.getName():
                if self.handler.parseIt:
                    self.handler.endRow()
                self.handler.startRow()
                self.handler.parseIt = True
            elif self.handler.parseIt:
                self.handler.parseGroup(groupCode, value)
