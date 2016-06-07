# Configuration of LasaurApp
#
# NOTE!
# -----
# To add/change config parameters create a file named
# userconfig.py and write something like this:
#
# conf = {
#     'network_port': 4411,
#     'serial_port': 'COM3'
# }
#

import os
import sys
import glob

conf = {
    'appname': 'lasaurapp',
    'version': '16.00-beta1',
    'company_name': 'com.nortd.labs',
    'network_host': '',          # '' for all nics
    'network_port': 4445,
    'websocket_port': 8989,
    'hardware': 'auto-detect', # 'auto-detect', 'standard', 'beaglebone' or 'raspberrypi'
    'serial_port': None, # something like '/dev/ttyACM0', '/dev/ttyUSB0' or 'COM3'
                         # can be None if on 'beaglebone' or 'raspberrypi' to use the default
    'baudrate': 57600,
    'baudrate_avrdude': None,
    'rootdir': None,     # defined further down (../)
    'stordir': None,     # defined further down
    'firmware': 'LasaurGrbl.hex',
    'tolerance': 0.01,
    'workspace': [12],
    # 'intensity_minmax': [0,255],
    'seekrate': 6000,
    'feedrate': 2000,
    'intensity': 0,
    'kerf': 0.3,
    'max_raster_size': [3000, 3000],
    'max_jobs_in_list': 20,
    'users': {
        'laser': 'laser',
    },

    'usb_reset_hack': False,
    'raster_leadin': 40,

    'max_segment_length': 5.0,

    'raster_size': 0.4,                 # size (mm) of beam for rastering
    'raster_offset': 40,
    'raster_feedrate': 3000,
    'raster_intensity': 20,
    'raster_linechars': 70,
}


### rootdir
# This is to be used with all relative file access.
# _MEIPASS is a special location for data files when creating
# standalone, single file python apps with pyInstaller.
# Standalone is created by calling from 'other' directory:
# python pyinstaller/pyinstaller.py --onefile app.spec
if hasattr(sys, "_MEIPASS"):
    conf['rootdir'] = sys._MEIPASS
else:
    # root is one up from this file
    conf['rootdir'] = os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))

### stordir
# This is to be used to store queue files and similar
if sys.platform == 'darwin':
    directory = os.path.join(os.path.expanduser('~'),
                             'Library', 'Application Support',
                             conf['company_name'], conf['appname'])
elif sys.platform == 'win32':
    directory = os.path.join(os.path.expandvars('%APPDATA%'),
                             conf['company_name'], conf['appname'])
else:
    directory = os.path.join(os.path.expanduser('~'), "." + conf['appname'])
if not os.path.exists(directory):
    os.makedirs(directory)
conf['stordir'] = directory


### overwrite conf with parameters from userconfig.py
try:
    import userconfig
    conf.update(userconfig.conf)
    print("Config: using userconfig.py")
except ImportError:
    print("Config: userconfig.py not found, using default configuration")


if conf['hardware'] == 'auto-detect':
    conf['hardware'] = 'standard'
    ### check if running on BBB
    # also works on old Beaglebone if named 'lasersaur'
    # os.uname() on BBB:
    # ('Linux', 'lasersaur', '3.8.13-bone20',
    #  '#1 SMP Wed May 29 06:14:59 UTC 2013', 'armv7l')
    uname = os.uname()
    if (sys.platform == "linux2"
            and (uname[1] == 'lasersaur' or uname[2] == '3.8.13-bone20')):
        conf['hardware'] = 'beaglebone'
    ### check if running on RaspberryPi
    try:
        import RPi.GPIO
        conf['hardware'] = 'raspberrypi'
    except ImportError:
        pass



## if running as root
#if os.geteuid() == 0:
#    conf['network_port'] = 80


if conf['serial_port'] is None:
    if conf['hardware'] == 'beaglebone':
        conf['serial_port'] = '/dev/ttyO1'
    elif conf['hardware'] == 'raspberrypi':
        conf['serial_port'] = '/dev/ttyAMA0'
    else:
        print('WARNING: serial_port is not configured. See backend/config.py for instructions.')
        conf['serial_port'] = "serial_port_not_configured"
