
__author__ = 'Andreas Bachmann <andreas.bachmann@fablabwinti.ch>'

import sys
print(sys.path)

import logging
from logging.config import fileConfig

fileConfig('log_config.ini')
log = logging.getLogger(__name__)

import filereaders.dxf.parser.dxf_parser
argc = len(sys.argv)
print("Number of arguments: " + str(argc))
for arg in sys.argv:
    print(arg)

log.debug("Open file")
f = open(sys.argv[1])

log.debug("Read file")
dxfstring = f.read()

log.debug("Parse content")
parser = filereaders.dxf.parser.dxf_parser.DXFParser()
list = parser.parse(dxfstring)


log.debug("Close file")
f.close()
