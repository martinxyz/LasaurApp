
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

from filereaders.dxf.util.point import Point

class DXFStringHeaderVariable(object):

    def __init__(self):
        self.string = ""

    def setString(self, string):
        self.string = string

    def getString(self):
        return self.string

class DXFVersionHeaderVariable(DXFStringHeaderVariable):

    VERSION_STR = {
        "MC0.0":            "AutoCAD Version 1.0",
        "AC1.2":            "AutoCAD Version 1.2",
        "AC1.40":           "AutoCAD Version 1.40",
        "AC1.50":           "AutoCAD Version 1.50",
        "AC2.10":           "AutoCAD Version 2.10",
        "AC2.21":           "AutoCAD Version 2.21",
        "AC2.22":           "AutoCAD Version 2.22",
        "AC1001":           "AutoCAD Version 2.22",
        "AC1002":           "AutoCAD Version 2.50",
        "AC1003":           "AutoCAD Version 2.60",
        "AC1004":           "AutoCAD Release 9",
        "AC1005":           "AutoCAD Pre-release 10",
        "AC1006":           "AutoCAD Release 10",
        "AC1007":           "AutoCAD Pre-release 11",
        "AC1008":           "AutoCAD Pre-release 11b",
        "AC1009":           "AutoCAD Release 11",
        "AC1010":           "AutoCAD Pre-release 13a",
        "AC1011":           "AutoCAD Pre-release 13b",
        "AC1012":           "AutoCAD Release 13",
        "AC1013":           "AutoCAD Pre-release 14",
        "AC1014":           "AutoCAD Release 14/14.01",
        "AC1500":           "AutoCAD Pre-release 2000",
        "AC1015":           "AutoCAD 2000",
        "AC1016":           "AutoCAD 2000i",
        "AC1017":           "AutoCAD 2002",
        "AC402a":           "AutoCAD Pre-release 2004a",
        "AC402b":           "AutoCAD Pre-release 2004b",
        "AC1018":           "AutoCAD 2004",
        "AC1019":           "AutoCAD 2005",
        "AC1020":           "AutoCAD 2006",
        "AC1021":           "AutoCAD 2007",
        "AC1022":           "AutoCAD 2008",
        "AC1023":           "AutoCAD 2009",
        "AC1024":           "AutoCAD 2010",
        "AC1025":           "AutoCAD 2011",
        "AC1026":           "AutoCAD 2012",
        "AC1027":           "AutoCAD 2013"
    }

    def __init__(self):
        super(DXFVersionHeaderVariable, self).__init__()

    def getVersion(self):
        try:
            version = self.VERSION_STR[self.string]
        except KeyError:
            version = "Unrecognized"
        return version

class DXFAngleHeaderVariable(object):

    def __init__(self):
        self.angle = 0.0

    def setAngle(self, angle):
        self.angle = angle

    def getAngle(self):
        return self.angle

class DXFIntegerHeaderVariable(object):

    def __init__(self):
        self.integer = 0

    def setInteger(self, integer):
        self.integer = integer

    def getInteger(self):
        return self.integer

class DXFColorHeaderVariable(object):

    def __init__(self):
        self.color = 0

    def setColor(self, color):
        self.color = color

    def getColor(self):
        return self.color



class DXFHeader:

    def __init__(self):
        self.version    = DXFVersionHeaderVariable()        #
        self.extMax     = Point()                           # X (10), Y (20), and Z (30) drawing extents upper-right corner (in WCS)
        self.extMin     = Point()                           # X (10), Y (20), and Z (30) drawing extents lower-left corner (in WCS)
        self.limMax     = Point()                           # X (10) and Y (20) drawing limits upper-right corner (in WCS)
        self.limMin     = Point()                           # X (10) and Y (20) drawing limits lower-left corner (in WCS)
        self.pExtMax    = Point()                           # Maximum X (10), Y (20), and Z (30) extents for paper space
        self.pExtMin    = Point()                           # Minimum X (10), Y (20), and Z (30) extents for paper space
        self.pLimMax    = Point()                           # Maximum X (10) and Y (20) limits in paper space
        self.pLimMin    = Point()                           # Minimum X (10) and Y (20) limits in paper space

