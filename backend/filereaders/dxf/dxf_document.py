
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from logging import Logger
from dxf_header import DXFHeader
from dxf_constants import DXFConstants


class DXFDocument:

    def __init__(self):
        from dxf_layer import DXFLayer
        self.header = DXFHeader()
        self.blocks = {}
        self.layers = {DXFConstants.DEFAULT_LAYER: DXFLayer(DXFConstants.DEFAULT_LAYER)}

    def getHeader(self):
        return self.header

    def getBlock(self, blockName):
        return self.blocks[blockName]

    def getLayer(self, layerName):
        """

        :param layerName:
        :type layerName: str
        :return:
        :rtype: filereaders.dxf.dxf_layer.DXFLayer
        """
        try:
            return self.layers[layerName]
        except KeyError:
            return self.layers[DXFConstants.DEFAULT_LAYER]

    def addLayer(self, layer):
        """

        :param layer:
        :type layer: filereaders.dxf.dxf_layer.DXFLayer
        """
        try:
            # don't overwrite layers with the same name
            tmp = self.layers[layer.getName()]
        except KeyError:
            self.layers[layer.getName()] = layer

    def addEntity(self, entity):
        """

        :param entity:
        :type: layer: filereaders.dxf.dxf_entity.DXFEntity
        """
        layer = self.getLayer(entity.getLayerName())
        layer.addEntity(entity)


