
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from . import dxf_handler
import logging


log = logging.getLogger(__name__)

class DXFParser(dxf_handler.DXFHandler):

    GROUP_CODE_ENTITY_START     = 0
    GROUP_CODE_NAME             = 2
    SECTION_START               = "SECTION"
    SECTION_END                 = "ENDSEC"
    EOF                         = "EOF"

    def __init__(self):
        from filereaders.dxf.parser.section.dxf_header_section_handler      import DXFHeaderSectionHandler
        from filereaders.dxf.parser.section.dxf_tables_section_handler      import DXFTablesSectionHandler
        from filereaders.dxf.parser.section.dxf_objects_section_handler     import DXFObjectsSectionHandler
        from filereaders.dxf.parser.section.dxf_entities_section_handler    import DXFEntitiesSectionHandler
        from filereaders.dxf.parser.table.dxf_application_id_handler        import DXFApplicationIdHandler
        from filereaders.dxf.parser.table.dxf_block_record_handler          import DXFBlockRecordHandler
        from filereaders.dxf.parser.table.dxf_dimension_style_handler       import DXFDimensionStyleHandler
        from filereaders.dxf.parser.table.dxf_layer_handler                 import DXFLayerHandler
        from filereaders.dxf.parser.table.dxf_line_type_handler             import DXFLineTypeHandler
        from filereaders.dxf.parser.table.dxf_ucs_handler                   import DXFUcsHandler
        from filereaders.dxf.parser.table.dxf_view_handler                  import DXFViewHandler
        from filereaders.dxf.parser.table.dxf_viewport_handler              import DXFViewportHandler
        from filereaders.dxf.parser.entities.dxf_arc_handler                import DXFArcHandler
        from filereaders.dxf.parser.entities.dxf_circle_handler             import DXFCircleHandler
        from filereaders.dxf.parser.entities.dxf_line_handler               import DXFLineHandler
        from filereaders.dxf.parser.entities.dxf_polyline_handler           import DXFPolylineHandler
        from filereaders.dxf.parser.entities.dxf_lwpolyline_handler         import DXFLwpolylineHandler
        from filereaders.dxf.parser.entities.dxf_spline_handler             import DXFSplineHandler

        super(DXFParser, self).__init__()

        self.addHandler(DXFHeaderSectionHandler())
        self.addHandler(DXFObjectsSectionHandler())

        handler = DXFTablesSectionHandler()
        handler.addHandler(DXFApplicationIdHandler())
        handler.addHandler(DXFBlockRecordHandler())
        handler.addHandler(DXFDimensionStyleHandler())
        handler.addHandler(DXFLayerHandler())
        handler.addHandler(DXFLineTypeHandler())
        handler.addHandler(DXFUcsHandler())
        handler.addHandler(DXFViewHandler())
        handler.addHandler(DXFViewportHandler())
        self.addHandler(handler)

        handler = DXFEntitiesSectionHandler()
        handler.addHandler(DXFArcHandler())
        handler.addHandler(DXFCircleHandler())
        handler.addHandler(DXFLineHandler())
        handler.addHandler(DXFPolylineHandler())
        handler.addHandler(DXFLwpolylineHandler())
        handler.addHandler(DXFSplineHandler())
        self.addHandler(handler)

        self.sectionStarts = False


    def parse(self, dxfstring, tolerance):
        from .dxf_group_buffer import DXFGroupBuffer
        from filereaders.dxf.dxf_document import DXFDocument

        linecount   = 0
        document    = DXFDocument()
        groupBuffer = DXFGroupBuffer(dxfstring)

        self.sectionStarts = False
        self.setDocument(document)

        for groupCode, value in groupBuffer:
            linecount += 1
            if not self.parseGroup(groupCode, value):
                break

        log.info("Parse Done")

        path = []
        for layerName, layer in document.layers.items():
            for entityName, entityList in layer.entities.items():
                try:
                    for entity in entityList:
                        path.append(entity.rasterize(tolerance))
                except NotImplementedError:
                    pass

        log.info("Rasterize Done")

        return path



    def parseGroup(self, groupCode, value):
        """
        :type  groupCode: int
        :type  value: filereaders.dxf.dxf_value.DXFValue
        """
        if groupCode == self.GROUP_CODE_ENTITY_START and value.getString() == self.EOF:
            return False

        elif groupCode == self.GROUP_CODE_ENTITY_START and value.getString() == self.SECTION_START:
            self.sectionStarts = True

        elif groupCode == self.GROUP_CODE_ENTITY_START and value.getString() == self.SECTION_END:
            if self.parseIt:
                self.handler.endSection()
            self.handler = None
            self.parseIt = False

        elif groupCode == self.GROUP_CODE_NAME and self.sectionStarts:
            self.sectionStarts = False
            try:
                self.handler = self.handlers[value.getString()]
                self.handler.setDocument(self.document)
                self.handler.startSection()
                self.parseIt = True
            except KeyError:
                self.parseIt = False

        elif self.parseIt:
            #try:
                self.handler.parseGroup(groupCode, value)
            #except AttributeError:
            #    raise AttributeError()

        return True