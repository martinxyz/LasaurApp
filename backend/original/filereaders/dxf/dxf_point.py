
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import dxf_entity
import dxf_constants


class DXFPoint(dxf_entity.DXFEntity):

    def __init__(self):
        super(DXFPoint, self).__init__()

    def getType(self):
        return dxf_constants.DXFConstants.ENTITY_TYPE_POINT
