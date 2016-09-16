
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import filereaders.dxf.util.vector


### General Group Codes
#    0 -    9   String
#   10 -   39   Double precision 3D point value
#   40 -   59   Double-precision floating-point value
#   60 -   79   16-bit integer value
#   90 -   99   32-bit integer value
#  100          String
#  102          String
#  105          String
#  110 -  119   Double precision floating-point value


### Header Variable Group Codes
#    1          Primary text value for an entity
#    2          Name (attribute tag, block name, and so on)
#    3          Other text or name values
#    5          Entity handle; text string of up to 16 hexadecimal digits
#    6          Linetype name
#    7          Text style name
#    8          Layer name
#   10          Primary point X
#   20          Primary point Y
#   30          Primary point Z
#   40          Double-precision floating-point values (text height, scale factors, and so on)
#   50          Angles (output in degrees to DXF files)
#   62          Color number
#   70          Integer values, such as repeat counts, flag bits, or modes
#  280          16-bit integer value
#  290          Boolean flag value
#  345,346,349  Hard-pointer handle; arbitrary hard pointers to other objects within same DXF file or drawing
#  370          Hard-owner handle; arbitrary hard ownership links to other objects within same DXF file or drawing
#  380          PlotStyleName type enum (AcDb::PlotStyleNameType). Stored and moved around as a 16-bit integer
#  390          String representing handle value of the PlotStyleName object, basically a hard pointer

class DXFConstants:

    def __init__(self):
        pass

    DEFAULT_LAYER                           = "0"
    DEFAULT_X_AXIS_VECTOR                   = filereaders.dxf.util.vector.Vector(1.0, 0.0, 0.0)
    DEFAULT_Y_AXIS_VECTOR                   = filereaders.dxf.util.vector.Vector(0.0, 1.0, 0.0)
    DEFAULT_Z_AXIS_VECTOR                   = filereaders.dxf.util.vector.Vector(0.0, 0.0, 1.0)


    SECTION_START                           = "SECTION"
    SECTION_END                             = "ENDSEC"

    SECTION_TYPE_BLOCKS                     = "BLOCKS"
    SECTION_TYPE_CLASSES                    = "CLASSES"
    SECTION_TYPE_ENTITIES                   = "ENTITIES"
    SECTION_TYPE_HEADER                     = "HEADER"
    SECTION_TYPE_OBJECTS                    = "OBJECTS"
    SECTION_TYPE_TABLES                     = "TABLES"
    SECTION_TYPE_THUMBNAILIMAGE             = "THUMBNAILIMAGE"

    ENTITY_TYPE_ARC                         = "ARC"
    ENTITY_TYPE_ATTRIB                      = "ATTRIB"
    ENTITY_TYPE_BODY                        = "BODY"
    ENTITY_TYPE_CIRCLE                      = "CIRCLE"
    ENTITY_TYPE_DIMENSION                   = "DIMENSION"
    ENTITY_TYPE_ELLIPSE                     = "ELLIPSE"
    ENTITY_TYPE_HATCH                       = "HATCH"
    ENTITY_TYPE_IMAGE                       = "IMAGE"
    ENTITY_TYPE_INSERT                      = "INSERT"
    ENTITY_TYPE_LEADER                      = "LEADER"
    ENTITY_TYPE_LINE                        = "LINE"
    ENTITY_TYPE_LWPOLYLINE                  = "LWPOLYLINE"
    ENTITY_TYPE_MLINE                       = "MLINE"
    ENTITY_TYPE_MTEXT                       = "MTEXT"
    ENTITY_TYPE_POINT                       = "POINT"
    ENTITY_TYPE_POLYLINE                    = "POLYLINE"
    ENTITY_TYPE_RAY                         = "RAY"
    ENTITY_TYPE_REGION                      = "REGION"
    ENTITY_TYPE_SHAPE                       = "SHAPE"
    ENTITY_TYPE_SOLID                       = "SOLID"
    ENTITY_TYPE_SPLINE                      = "SPLINE"
    ENTITY_TYPE_TABLE                       = "TABLE"
    ENTITY_TYPE_TEXT                        = "TEXT"
    ENTITY_TYPE_TOLERANCE                   = "TOLERANCE"
    ENTITY_TYPE_TRACE                       = "TRACE"
    ENTITY_TYPE_VERTEX                      = "VERTEX"
    ENTITY_TYPE_VIEWPORT                    = "VIEWPORT"
    ENTITY_TYPE_XLINE                       = "XLINE"

    TABLE_TYPE_APPLICATION_ID               = "APPID"
    TABLE_TYPE_BLOCK_RECORD                 = "BLOCK_RECORD"
    TABLE_TYPE_DIMENSION_STYLE              = "DIMSTYLE"
    TABLE_TYPE_LAYER                        = "LAYER"
    TABLE_TYPE_LINE_TYPE                    = "LTYPE"
    TABLE_TYPE_TEXT_STYLE                   = "STYLE"
    TABLE_TYPE_UCS                          = "UCS"
    TABLE_TYPE_VIEW                         = "VIEW"
    TABLE_TYPE_VIEWPORT                     = "VPORT"

    HEADER_VARIABLE_ACADMAINTVER            = "$ACADMAINTVER"           # Maintenance version number
    HEADER_VARIABLE_ACADVER                 = "$ACADVER"                # The AutoCAD drawing database version number
    HEADER_VARIABLE_ANGBASE                 = "$ANGBASE"                # Angle (50 = Angle)
    HEADER_VARIABLE_ANGDIR                  = "$ANGDIR"                 # Angle direction (70 = Integer):
                                                                        #   1 = Clockwise angles,
                                                                        #   0 = Counterclockwise angles
    HEADER_VARIABLE_ATTMODE                 = "$ATTMODE"                # Attribute visibility (70 = Integer):
                                                                        #   0 = None
                                                                        #   1 = Normal
                                                                        #   2 = All
    HEADER_VARIABLE_AUNITS                  = "$AUNITS"                 # Units format for angles (70 = Integer)
    HEADER_VARIABLE_AUPREC                  = "$AUPREC"                 # Units precision for angles (70 = Integer)
    HEADER_VARIABLE_CECOLOR                 = "$CECOLOR"                # Current entity color number (62 = Color number):
                                                                        #   0 = BYBLOCK
                                                                        # 256 = BYLAYER
    HEADER_VARIABLE_CELTSCALE               = "$CELTSCALE"
    HEADER_VARIABLE_CELTYPE                 = "$CELTYPE"
    HEADER_VARIABLE_CELWEIGHT               = "$CELWEIGHT"
    HEADER_VARIABLE_CEPSNID                 = "$CEPSNID"
    HEADER_VARIABLE_CEPSNTYPE               = "$CEPSNTYPE"
    HEADER_VARIABLE_CHAMFERA                = "$CHAMFERA"
    HEADER_VARIABLE_CHAMFERB                = "$CHAMFERB"
    HEADER_VARIABLE_CHAMFERC                = "$CHAMFERC"
    HEADER_VARIABLE_CHAMFERD                = "$CHAMFERD"
    HEADER_VARIABLE_CLAYER                  = "$CLAYER"
    HEADER_VARIABLE_CMLJUST                 = "$CMLJUST"
    HEADER_VARIABLE_CMLSCALE                = "$CMLSCALE"
    HEADER_VARIABLE_CMLSTYLE                = "$CMLSTYLE"
    HEADER_VARIABLE_DIMADEC                 = "$DIMADEC"
    HEADER_VARIABLE_DIMALT                  = "$DIMALT"
    HEADER_VARIABLE_DIMALTD                 = "$DIMALTD"
    HEADER_VARIABLE_DIMALTF                 = "$DIMALTF"
    HEADER_VARIABLE_DIMALTRND               = "$DIMALTRND"
    HEADER_VARIABLE_DIMALTTD                = "$DIMALTTD"
    HEADER_VARIABLE_DIMALTTZ                = "$DIMALTTZ"
    HEADER_VARIABLE_DIMALTU                 = "$DIMALTU"
    HEADER_VARIABLE_DIMALTZ                 = "$DIMALTZ"
    HEADER_VARIABLE_DIMAPOST                = "$DIMAPOST"
    HEADER_VARIABLE_DIMASO                  = "$DIMASO"
    HEADER_VARIABLE_DIMASSOC                = "$DIMASSOC"
    HEADER_VARIABLE_DIMASZ                  = "$DIMASZ"
    HEADER_VARIABLE_DIMATFIT                = "$DIMATFIT"
    HEADER_VARIABLE_DIMAUNIT                = "$DIMAUNIT"
    HEADER_VARIABLE_DIMAZIN                 = "$DIMAZIN"
    HEADER_VARIABLE_DIMBLK                  = "$DIMBLK"
    HEADER_VARIABLE_DIMBLK1                 = "$DIMBLK1"
    HEADER_VARIABLE_DIMCEN                  = "$DIMCEN"
    HEADER_VARIABLE_DIMCLRD                 = "$DIMCLRD"
    HEADER_VARIABLE_DIMCLRE                 = "$DIMCLRE"
    HEADER_VARIABLE_DIMCLRT                 = "$DIMCLRT"
    HEADER_VARIABLE_DIMDEC                  = "$DIMDEC"
    HEADER_VARIABLE_DIMDLE                  = "$DIMDLE"
    HEADER_VARIABLE_DIMDLI                  = "$DIMDLI"
    HEADER_VARIABLE_DIMDSEP                 = "$DIMDSEP"
    HEADER_VARIABLE_DIMEXE                  = "$DIMEXE"
    HEADER_VARIABLE_DIMEXO                  = "$DIMEXO"
    HEADER_VARIABLE_DIMFAC                  = "$DIMFAC"
    HEADER_VARIABLE_DIMGAP                  = "$DIMGAP"
    HEADER_VARIABLE_DIMJUST                 = "$DIMJUST"
    HEADER_VARIABLE_DIMLDRBLK               = "$DIMLDRBLK"
    HEADER_VARIABLE_DIMLFAC                 = "$DIMLFAC"
    HEADER_VARIABLE_DIMLIM                  = "$DIMLIM"
    HEADER_VARIABLE_DIMLUNIT                = "$DIMLUNIT"
    HEADER_VARIABLE_DIMLWD                  = "$DIMLWD"
    HEADER_VARIABLE_DIMLWE                  = "$DIMLWE"
    HEADER_VARIABLE_DIMPOST                 = "$DIMPOST"
    HEADER_VARIABLE_DIMRND                  = "$DIMRND"
    HEADER_VARIABLE_DIMSAH                  = "$DIMSAH"
    HEADER_VARIABLE_DIMSCALE                = "$DIMSCALE"
    HEADER_VARIABLE_DIMSD1                  = "$DIMSD1"
    HEADER_VARIABLE_DIMSD2                  = "$DIMSD2"
    HEADER_VARIABLE_DIMSE1                  = "$DIMSE1"
    HEADER_VARIABLE_DIMSE2                  = "$DIMSE2"
    HEADER_VARIABLE_DIMSHO                  = "$DIMSHO"
    HEADER_VARIABLE_DIMSOXD                 = "$DIMSOXD"
    HEADER_VARIABLE_DIMSTYLE                = "$DIMSTYLE"
    HEADER_VARIABLE_DIMTAD                  = "$DIMTAD"
    HEADER_VARIABLE_DIMTDEC                 = "$DIMTDEC"
    HEADER_VARIABLE_DIMTFAC                 = "$DIMTFAC"
    HEADER_VARIABLE_DIMTIH                  = "$DIMTIH"
    HEADER_VARIABLE_DIMTIX                  = "$DIMTIX"
    HEADER_VARIABLE_DIMTM                   = "$DIMTM"
    HEADER_VARIABLE_DIMTMOVE                = "$DIMTMOVE"
    HEADER_VARIABLE_DIMTOFL                 = "$DIMTOFL"
    HEADER_VARIABLE_DIMTOH                  = "$DIMTOH"
    HEADER_VARIABLE_DIMTOL                  = "$DIMTOL"
    HEADER_VARIABLE_DIMTOLJ                 = "$DIMTOLJ"
    HEADER_VARIABLE_DIMTP                   = "$DIMTP"
    HEADER_VARIABLE_DIMTSZ                  = "$DIMTSZ"
    HEADER_VARIABLE_DIMTVP                  = "$DIMTVP"
    HEADER_VARIABLE_DIMTXSTY                = "$DIMTXSTY"
    HEADER_VARIABLE_DIMTXT                  = "$DIMTXT"
    HEADER_VARIABLE_DIMTZIN                 = "$DIMTZIN"
    HEADER_VARIABLE_DIMUPT                  = "$DIMUPT"
    HEADER_VARIABLE_DIMZIN                  = "$DIMZIN"
    HEADER_VARIABLE_DISPSILH                = "$DISPSILH"
    HEADER_VARIABLE_DWGCODEPAGE             = "$DWGCODEPAGE"
    HEADER_VARIABLE_ELEVATION               = "$ELEVATION"
    HEADER_VARIABLE_ENDCAPS                 = "$ENDCAPS"
    HEADER_VARIABLE_EXTMAX                  = "$EXTMAX"
    HEADER_VARIABLE_EXTMIN                  = "$EXTMIN"
    HEADER_VARIABLE_EXTNAMES                = "$EXTNAMES"
    HEADER_VARIABLE_FASTZOOM                = "$FASTZOOM"
    HEADER_VARIABLE_FILLETRAD               = "$FILLETRAD"
    HEADER_VARIABLE_FILLMODE                = "$FILLMODE"
    HEADER_VARIABLE_FINGERPRINTGUID         = "$FINGERPRINTGUID"
    HEADER_VARIABLE_GRIDMODE                = "$GRIDMODE"
    HEADER_VARIABLE_GRIDUNIT                = "$GRIDUNIT"
    HEADER_VARIABLE_HALOGAP                 = "$HALOGAP"
    HEADER_VARIABLE_HANDSEED                = "$HANDSEED"
    HEADER_VARIABLE_HIDETEXT                = "$HIDETEXT"
    HEADER_VARIABLE_HYPERLINKBASE           = "$HYPERLINKBASE"
    HEADER_VARIABLE_INDEXCTL                = "$INDEXCTL"
    HEADER_VARIABLE_INSBASE                 = "$INSBASE"
    HEADER_VARIABLE_INSUNITS                = "$INSUNITS"
    HEADER_VARIABLE_INTERSECTIONCOLOR       = "$INTERSECTIONCOLOR"
    HEADER_VARIABLE_INTERSECTIONDISPLAY     = "$INTERSECTIONDISPLAY"
    HEADER_VARIABLE_JOINSTYLE               = "$JOINSTYLE"
    HEADER_VARIABLE_LIMCHECK                = "$LIMCHECK"
    HEADER_VARIABLE_LIMMAX                  = "$LIMMAX"
    HEADER_VARIABLE_LIMMIN                  = "$LIMMIN"
    HEADER_VARIABLE_LTSCALE                 = "$LTSCALE"
    HEADER_VARIABLE_LUNITS                  = "$LUNITS"
    HEADER_VARIABLE_LUPREC                  = "$LUPREC"
    HEADER_VARIABLE_LWDISPLAY               = "$LWDISPLAY"
    HEADER_VARIABLE_MAXACTVP                = "$MAXACTVP"
    HEADER_VARIABLE_MEASUREMENT             = "$MEASUREMENT"
    HEADER_VARIABLE_MENU                    = "$MENU"
    HEADER_VARIABLE_MIRRTEXT                = "$MIRRTEXT"
    HEADER_VARIABLE_OBSCOLOR                = "$OBSCOLOR"
    HEADER_VARIABLE_OBSLTYPE                = "$OBSLTYPE"
    HEADER_VARIABLE_ORTHOMODE               = "$ORTHOMODE"
    HEADER_VARIABLE_PDMODE                  = "$PDMODE"
    HEADER_VARIABLE_PDSIZE                  = "$PDSIZE"
    HEADER_VARIABLE_PELEVATION              = "$PELEVATION"
    HEADER_VARIABLE_PEXTMAX                 = "$PEXTMAX"
    HEADER_VARIABLE_PEXTMIN                 = "$PEXTMIN"
    HEADER_VARIABLE_PINSBASE                = "$PINSBASE"
    HEADER_VARIABLE_PLIMCHECK               = "$PLIMCHECK"
    HEADER_VARIABLE_PLIMMAX                 = "$PLIMMAX"
    HEADER_VARIABLE_PLIMMIN                 = "$PLIMMIN"
    HEADER_VARIABLE_PLINEGEN                = "$PLINEGEN"
    HEADER_VARIABLE_PLINEWID                = "$PLINEWID"
    HEADER_VARIABLE_PROJECTNAME             = "$PROJECTNAME"
    HEADER_VARIABLE_PROXYGRAPHICS           = "$PROXYGRAPHICS"
    HEADER_VARIABLE_PSLTSCALE               = "$PSLTSCALE"
    HEADER_VARIABLE_PSTYLEMODE              = "$PSTYLEMODE"
    HEADER_VARIABLE_PSVPSCALE               = "$PSVPSCALE"
    HEADER_VARIABLE_PUCSBASE                = "$PUCSBASE"
    HEADER_VARIABLE_PUCSNAME                = "$PUCSNAME"
    HEADER_VARIABLE_PUCSORG                 = "$PUCSORG"
    HEADER_VARIABLE_PUCSORGBACK             = "$PUCSORGBACK"
    HEADER_VARIABLE_PUCSORGBOTTOM           = "$PUCSORGBOTTOM"
    HEADER_VARIABLE_PUCSORGFRONT            = "$PUCSORGFRONT"
    HEADER_VARIABLE_PUCSORGLEFT             = "$PUCSORGLEFT"
    HEADER_VARIABLE_PUCSORGRIGHT            = "$PUCSORGRIGHT"
    HEADER_VARIABLE_PUCSORGTOP              = "$PUCSORGTOP"
    HEADER_VARIABLE_PUCSORTHOREF            = "$PUCSORTHOREF"
    HEADER_VARIABLE_PUCSORTHOVIEW           = "$PUCSORTHOVIEW"
    HEADER_VARIABLE_PUCSXDIR                = "$PUCSXDIR"
    HEADER_VARIABLE_PUCSYDIR                = "$PUCSYDIR"
    HEADER_VARIABLE_QTEXTMODE               = "$QTEXTMODE"
    HEADER_VARIABLE_REGENMODE               = "$REGENMODE"
    HEADER_VARIABLE_SHADEDGE                = "$SHADEDGE"
    HEADER_VARIABLE_SHADEDIF                = "$SHADEDIF"
    HEADER_VARIABLE_SKETCHINC               = "$SKETCHINC"
    HEADER_VARIABLE_SKPOLY                  = "$SKPOLY"
    HEADER_VARIABLE_SNAPANG                 = "$SNAPANG"
    HEADER_VARIABLE_SNAPBASE                = "$SNAPBASE"
    HEADER_VARIABLE_SNAPISOPAIR             = "$SNAPISOPAIR"
    HEADER_VARIABLE_SNAPMODE                = "$SNAPMODE"
    HEADER_VARIABLE_SNAPSTYLE               = "$SNAPSTYLE"
    HEADER_VARIABLE_SNAPUNIT                = "$SNAPUNIT"
    HEADER_VARIABLE_SORTENTS                = "$SORTENTS"
    HEADER_VARIABLE_SPLFRAME                = "$SPLFRAME"
    HEADER_VARIABLE_SPLINESEGS              = "$SPLINESEGS"
    HEADER_VARIABLE_SPLINETYPE              = "$SPLINETYPE"
    HEADER_VARIABLE_SURFTAB1                = "$SURFTAB1"
    HEADER_VARIABLE_SURFTAB2                = "$SURFTAB2"
    HEADER_VARIABLE_SURFTYPE                = "$SURFTYPE"
    HEADER_VARIABLE_SURFU                   = "$SURFU"
    HEADER_VARIABLE_SURFV                   = "$SURFV"
    HEADER_VARIABLE_TDCREATE                = "$TDCREATE"
    HEADER_VARIABLE_TDINDWG                 = "$TDINDWG"
    HEADER_VARIABLE_TDUCREATE               = "$TDUCREATE"
    HEADER_VARIABLE_TDUPDATE                = "$TDUPDATE"
    HEADER_VARIABLE_TDUSRTIMER              = "$TDUSRTIMER"
    HEADER_VARIABLE_TDUUPDATE               = "$TDUUPDATE"
    HEADER_VARIABLE_TEXTSIZE                = "$TEXTSIZE"
    HEADER_VARIABLE_TEXTSTYLE               = "$TEXTSTYLE"
    HEADER_VARIABLE_THICKNESS               = "$THICKNESS"
    HEADER_VARIABLE_TILEMODE                = "$TILEMODE"
    HEADER_VARIABLE_TRACEWID                = "$TRACEWID"
    HEADER_VARIABLE_TREEDEPTH               = "$TREEDEPTH"
    HEADER_VARIABLE_UCSBASE                 = "$UCSBASE"
    HEADER_VARIABLE_UCSNAME                 = "$UCSNAME"
    HEADER_VARIABLE_UCSORG                  = "$UCSORG"
    HEADER_VARIABLE_UCSORGBACK              = "$UCSORGBACK"
    HEADER_VARIABLE_UCSORGBOTTOM            = "$UCSORGBOTTOM"
    HEADER_VARIABLE_UCSORGFRONT             = "$UCSORGFRONT"
    HEADER_VARIABLE_UCSORGLEFT              = "$UCSORGLEFT"
    HEADER_VARIABLE_UCSORGRIGHT             = "$UCSORGRIGHT"
    HEADER_VARIABLE_UCSORGTOP               = "$UCSORGTOP"
    HEADER_VARIABLE_UCSORTHOREF             = "$UCSORTHOREF"
    HEADER_VARIABLE_UCSORTHOVIEW            = "$UCSORTHOVIEW"
    HEADER_VARIABLE_UCSXDIR                 = "$UCSXDIR"
    HEADER_VARIABLE_UCSYDIR                 = "$UCSYDIR"
    HEADER_VARIABLE_UNITMODE                = "$UNITMODE"
    HEADER_VARIABLE_USERI1                  = "$USERI1"
    HEADER_VARIABLE_USERR1                  = "$USERR1"
    HEADER_VARIABLE_USRTIMER                = "$USRTIMER"
    HEADER_VARIABLE_VERSIONGUID             = "$VERSIONGUID"
    HEADER_VARIABLE_VIEWCTR                 = "$VIEWCTR"
    HEADER_VARIABLE_VIEWDIR                 = "$VIEWDIR"
    HEADER_VARIABLE_VIEWSIZE                = "$VIEWSIZE"
    HEADER_VARIABLE_VISRETAIN               = "$VISRETAIN"
    HEADER_VARIABLE_WORLDVIEW               = "$WORLDVIEW"
    HEADER_VARIABLE_XCLIPFRAME              = "$XCLIPFRAME"
    HEADER_VARIABLE_XEDIT                   = "$XEDIT"
