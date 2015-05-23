
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'


class DXFHandler(object):

    def __init__(self, name = ""):
        self.name     = name
        self.document = None
        self.handlers = {}
        self.handler  = None
        self.parseIt  = False

    def getName(self):
        return self.name

    def setDocument(self, document):
        """

        :param document:
        :type document: filereaders.dxf.dxf_document.DXFDocument
        """
        self.document = document

    def addHandler(self, handler):
        """

        :param handler:
        :type handler: filereaders.dxf.dxf_handler.DXFHandler
        """
        self.handlers[handler.getName()] = handler

    def parseGroup(self, groupCode, value):
        """

        :param groupCode:
        :param value:
        :type groupCode: int
        :type value: filereaders.dxf.dxf_value.DXFValue
        :return: None
        """
        pass
