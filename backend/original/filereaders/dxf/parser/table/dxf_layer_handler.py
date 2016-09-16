
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.parser.table import dxf_table_handler
from filereaders.dxf.dxf_layer import DXFLayer

# Layer (LAYER) table
class DXFLayerHandler(dxf_table_handler.DXFTableHandler):

    GROUP_CODE_LAYER_NAME                       = 2
    GROUP_CODE_ELEMENT_REFERENCE                = 5
    GROUP_CODE_LAYER_LINE_TYPE                  = 6
    GROUP_CODE_LAYER_COLOR_NUMBER               = 62
    GROUP_CODE_LAYER_STANDARD_FLAGS             = 70
    GROUP_CODE_LAYER_PLOTTING_FLAG              = 290
    GROUP_CODE_LAYER_LINE_WEIGHT                = 370
    GROUP_CODE_LAYER_PLOT_STYLE_NAME            = 390

    def __init__(self):
        from filereaders.dxf.dxf_constants import DXFConstants

        super(DXFLayerHandler, self).__init__(DXFConstants.TABLE_TYPE_LAYER)

        self.layer = None

    def startTable(self):
        super(DXFLayerHandler, self).startTable()

    def endTable(self):
        super(DXFLayerHandler, self).endTable()

    def startRow(self):
        super(DXFLayerHandler, self).startRow()
        self.layer = DXFLayer()

    def endRow(self):
        super(DXFLayerHandler, self).endRow()
        self.document.addLayer(self.layer)

    def parseGroup(self, groupCode, value):
        if groupCode == self.GROUP_CODE_LAYER_NAME:
            self.layer.setName(value.getString())

        elif groupCode == self.GROUP_CODE_ELEMENT_REFERENCE:
            self.layer.setReference(value.getString())

        elif groupCode == self.GROUP_CODE_LAYER_LINE_TYPE:
            self.layer.setLineType(value.getString())

        elif groupCode == self.GROUP_CODE_LAYER_COLOR_NUMBER:
            self.layer.setColor(value.getInt())

        elif groupCode == self.GROUP_CODE_LAYER_PLOTTING_FLAG:
            pass

        elif groupCode == self.GROUP_CODE_LAYER_LINE_WEIGHT:
            self.layer.setLineWeight(value.getInt())

        elif groupCode == self.GROUP_CODE_LAYER_PLOT_STYLE_NAME:
            self.layer.setPlotStyle(value.getString())

