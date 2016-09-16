
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import filereaders.dxf.parser.dxf_handler

class DXFEntityHandler(filereaders.dxf.parser.dxf_handler.DXFHandler):

    GROUP_CODE_ENTITY_START         = 0         # LINE, CIRCLE, ARC, ...
    GROUP_CODE_ELEMENT_REFERENCE    = 5
    GROUP_CODE_SOFT_POINTER         = 330
    GROUP_CODE_ENTITIES_FOLLOW      = 66        # Obsolete
    GROUP_CODE_SUBCLASS_MARKER      = 100       # AcDbEntity
    GROUP_CODE_START_X              = 10
    GROUP_CODE_START_Y              = 20
    GROUP_CODE_START_Z              = 30
    GROUP_CODE_END_X                = 11
    GROUP_CODE_END_Y                = 21
    GROUP_CODE_END_Z                = 31
    GROUP_CODE_LAYER_NAME           = 8
    GROUP_CODE_TRANSPARENCY         = 440
    GROUP_CODE_COLOR_CODE           = 62
    GROUP_CODE_COLORNAME            = 430
    GROUP_CODE_COLOR_24BIT          = 420
    GROUP_CODE_COLOR_TRANSPARENCY   = 440
    GROUP_CODE_FLAGS                = 70
    GROUP_CODE_EXTRUSION_X          = 210
    GROUP_CODE_EXTRUSION_Y          = 220
    GROUP_CODE_EXTRUSION_Z          = 230
    GROUP_CODE_VISIBILITY           = 60
    GROUP_CODE_LINE_TYPE            = 6
    GROUP_CODE_LINE_TYPE_SCALE      = 48
    GROUP_CODE_LINE_WEIGHT          = 370
    GROUP_CODE_THICKNESS            = 39
    GROUP_CODE_STYLENAME            = 3
    GROUP_CODE_TEXT                 = 1
    GROUP_CODE_ROTATION_ANGLE       = 50
    GROUP_CODE_MODELSPACE           = 67

    def __init__(self, name):
        super(DXFEntityHandler, self).__init__(name)

    def getEntity(self):
        pass

    def startEntity(self):
        self.parseIt = True

    def endEntity(self):
        if self.parseIt:
            self.document.addEntity(self.getEntity())


    def hasFollowingSequence(self):
        """
        :return: return true if the this DXFEntityHandler have to parse the following
                 entities (like POLYLINE), otherwise false (like TEXT,LINE).
        :rtype: Bool
        """
        return False


    def parseCommonProperty(self, groupCode, value, entity):
        if groupCode == self.GROUP_CODE_ELEMENT_REFERENCE:
            entity.setId(value.getString())

        elif groupCode == self.GROUP_CODE_SOFT_POINTER:
            #entity.set...(value.getString())
            pass

        elif groupCode == self.GROUP_CODE_LAYER_NAME:
            entity.setLayerName(value.getString())

        elif groupCode == self.GROUP_CODE_FLAGS:
            entity.setFlags(value.getInt())

        elif groupCode == self.GROUP_CODE_VISIBILITY:
            entity.setVisibile(not value.getBooleanValue())

        elif groupCode == self.GROUP_CODE_LINE_TYPE:
            entity.setLineType(value.getString())

        elif groupCode == self.GROUP_CODE_LINE_TYPE_SCALE:
            entity.setLineTypeScaleFactor(value.getDouble())

        elif groupCode == self.GROUP_CODE_COLOR_CODE:
            entity.setColor(value.getInt())

        elif groupCode == self.GROUP_CODE_EXTRUSION_X:
            entity.setExtrusionX(value.getDouble())

        elif groupCode == self.GROUP_CODE_EXTRUSION_Y:
            entity.setExtrusionY(value.getDouble())

        elif groupCode == self.GROUP_CODE_EXTRUSION_Z:
            entity.setExtrusionZ(value.getDouble())

        elif groupCode == self.GROUP_CODE_COLOR_24BIT:
            pass

        elif groupCode == self.GROUP_CODE_COLOR_TRANSPARENCY:
            pass

        elif groupCode == self.GROUP_CODE_LINE_WEIGHT:
            entity.setLineWeight(value.getInt())

        elif groupCode == self.GROUP_CODE_THICKNESS:
            entity.setThickness(value.getDouble())

        elif groupCode == self.GROUP_CODE_MODELSPACE:
            #entity.setModelSpace(value.getBooleanValue())
            pass


