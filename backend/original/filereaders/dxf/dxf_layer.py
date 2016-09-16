
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.util.vector import Vector


class DXFLayer(object):
    # layers = 0
    # viewports = 0
    # bounds = 0
    # margin = 0
    # header = 0

    def __init__(self, name = "", document = None):
        """

        :param name:
        :param document:
        :type name: str
        :type document: filereaders.dxf.dxf_document.DXFDocument
        """
        self.name = name
        self.document = document
        self.reference = ""
        self.entities = {}
        self.color = 0
        self.lineType = ""
        self.lineWeight = 0
        self.plotStyle = ""

    def setName(self, name):
        """

        :param name:
        :type name: str
        """
        self.name = name

    def getName(self):
        """

        :return:
        :rtype: str
        """
        return self.name

    def setDocument(self, document):
        """

        :param document:
        :type: filereaders.dxf.dxf_document.DXFDocument
        """
        self.document = document

    def getDocument(self):
        """

        :return:
        :rtype: filereaders.dxf.dxf_document.DXFDocument
        """
        return self.document

    def addEntity(self, entity):
        typeList = None
        try:
            typeList = self.entities[entity.getType()]
            typeList.append(entity)
        except KeyError:
            typeList = [entity]
            self.entities[entity.getType()] = typeList

    def setReference(self, reference):
        self.reference = reference

    def getReference(self):
        return self.reference

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color

    def setLineType(self, lineType):
        self.lineType = lineType

    def getLineType(self):
        return self.lineType

    def setLineWeight(self, lineWeight):
        self.lineWeight = lineWeight

    def getLineWeight(self):
        return self.lineWeight

    def setPlotStyle(self, plotStyle):
        self.plotStyle = plotStyle

    def getPlotStyle(self):
        return self.plotStyle

