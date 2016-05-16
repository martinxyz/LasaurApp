
import sys, os, time
import glob, json, argparse, copy
import tempfile
import socket, webbrowser
from wsgiref.simple_server import WSGIRequestHandler, make_server
from bottle import *
from serial_manager import SerialManager
from filereaders import read_svg, read_dxf, read_ngc


APPNAME = "lasaurapp"
VERSION = "14.11b"
COMPANY_NAME = "com.nortd.labs"
SERIAL_PORT = None
BITSPERSECOND = 57600
NETWORK_PORT = 4444
HARDWARE = 'x86'  # also: 'beaglebone', 'raspberrypi'
CONFIG_FILE = "lasaurapp.conf"
COOKIE_KEY = 'secret_key_jkn23489hsdf'
FIRMWARE = "LasaurGrbl.hex"
TOLERANCE = 0.08


def resources_dir():
    """This is to be used with all relative file access.
       _MEIPASS is a special location for data files when creating
       standalone, single file python apps with pyInstaller.
       Standalone is created by calling from 'other' directory:
       python pyinstaller/pyinstaller.py --onefile app.spec
    """
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        # root is one up from this file
        return os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../'))


def storage_dir():
    directory = ""
    if sys.platform == 'darwin':
        # from AppKit import NSSearchPathForDirectoriesInDomains
        # # NSApplicationSupportDirectory = 14
        # # NSUserDomainMask = 1
        # # True for expanding the tilde into a fully qualified path
        # appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME)
        directory = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', COMPANY_NAME, APPNAME)
    elif sys.platform == 'win32':
        directory = os.path.join(os.path.expandvars('%APPDATA%'), COMPANY_NAME, APPNAME)
    else:
        directory = os.path.join(os.path.expanduser('~'), "." + APPNAME)

    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory


class HackedWSGIRequestHandler(WSGIRequestHandler):
    """ This is a heck to solve super slow request handling
    on the BeagleBone and RaspberryPi. The problem is WSGIRequestHandler
    which does a reverse lookup on every request calling gethostbyaddr.
    For some reason this is super slow when connected to the LAN.
    (adding the IP and name of the requester in the /etc/hosts file
    solves the problem but obviously is not practical)
    """
    def address_string(self):
        """Instead of calling getfqdn -> gethostbyaddr we ignore."""
        # return "(a requester)"
        return str(self.client_address[0])

    def log_request(*args, **kw):
        # if debug:
            # return wsgiref.simple_server.WSGIRequestHandler.log_request(*args, **kw)
        pass


def run_with_callback(host, port):
    """ Start a wsgiref server instance with control over the main loop.
        This is a function that I derived from the bottle.py run()
    """
    handler = default_app()
    server = make_server(host, port, handler, handler_class=HackedWSGIRequestHandler)
    server.timeout = 0.01
    server.quiet = True
    print("Persistent storage root is: " + storage_dir())
    print("-----------------------------------------------------------------------------")
    print("Bottle server starting up ...")
    print("Serial is set to %d bps" % BITSPERSECOND)
    print("Point your browser to: ")
    print("http://%s:%d/      (local)" % ('127.0.0.1', port))
    # if host == '':
    #     try:
    #         print "http://%s:%d/   (public)" % (socket.gethostbyname(socket.gethostname()), port)
    #     except socket.gaierror:
    #         # print "http://beaglebone.local:4444/      (public)"
    #         pass
    print("Use Ctrl-C to quit.")
    print("-----------------------------------------------------------------------------")
    print()
    ## open web-browser
    #try:
    #    webbrowser.open_new_tab('http://127.0.0.1:'+str(port))
    #except webbrowser.Error:
    #    print "Cannot open Webbrowser, please do so manually."
    sys.stdout.flush()  # make sure everything gets flushed
    server.timeout = 0
    while 1:
        try:
            SerialManager.send_queue_as_ready()
            server.handle_request()
            time.sleep(0.050)
        except KeyboardInterrupt:
            break
    print("\nBottle server shutting down...")
    SerialManager.close()




# @route('/longtest')
# def longtest_handler():
#     fp = open("longtest.ngc")
#     for line in fp:
#         SerialManager.queue_gcode_line(line)
#     return "Longtest queued."



@route('/css/:path#.+#')
def static_css_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/original/css'))

@route('/js/:path#.+#')
def static_js_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/original/js'))

@route('/img/:path#.+#')
def static_img_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'frontend/original/img'))

@route('/favicon.ico')
def favicon_handler():
    return static_file('favicon.ico', root=os.path.join(resources_dir(), 'frontend/original/img'))


### LIBRARY

@route('/library/get/:path#.+#')
def static_library_handler(path):
    return static_file(path, root=os.path.join(resources_dir(), 'library'), mimetype='text/plain')

@route('/library/list')
def library_list_handler():
    # return a json list of file names
    file_list = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(os.path.join(resources_dir(), 'library'))
        file_list = glob.glob('*')
    finally:
        os.chdir(cwd_temp)
    return json.dumps(file_list)



### QUEUE

def encode_filename(name):
    str(time.time()) + '-' + base64.urlsafe_b64encode(name)

def decode_filename(name):
    index = name.find('-')
    return base64.urlsafe_b64decode(name[index+1:])


@route('/queue/get/:name#.+#')
def static_queue_handler(name):
    return static_file(name, root=storage_dir(), mimetype='text/plain')


@route('/queue/list')
def library_list_handler():
    # base64.urlsafe_b64encode()
    # base64.urlsafe_b64decode()
    # return a json list of file names
    files = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(storage_dir())
        files = list(filter(os.path.isfile, glob.glob("*")))
        files.sort(key=lambda x: os.path.getmtime(x))
    finally:
        os.chdir(cwd_temp)
    return json.dumps(files)

@route('/queue/save', method='POST')
def queue_save_handler():
    ret = '0'
    if 'job_name' in request.forms and 'job_data' in request.forms:
        name = request.forms.get('job_name')
        job_data = request.forms.get('job_data')
        filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
        if os.path.exists(filename) or os.path.exists(filename+'.starred'):
            return "file_exists"
        try:
            fp = open(filename, 'w')
            fp.write(job_data)
            print("file saved: " + filename)
            ret = '1'
        finally:
            fp.close()
    else:
        print("error: save failed, invalid POST request")
    return ret

@route('/queue/rm/:name')
def queue_rm_handler(name):
    # delete queue item, on success return '1'
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename):
            try:
                os.remove(filename);
                print("file deleted: " + filename)
                ret = '1'
            finally:
                pass
    return ret

@route('/queue/clear')
def queue_clear_handler():
    # delete all queue items, on success return '1'
    ret = '0'
    files = []
    cwd_temp = os.getcwd()
    try:
        os.chdir(storage_dir())
        files = list(filter(os.path.isfile, glob.glob("*")))
        files.sort(key=lambda x: os.path.getmtime(x))
    finally:
        os.chdir(cwd_temp)
    for filename in files:
        if not filename.endswith('.starred'):
            filename = os.path.join(storage_dir(), filename)
            try:
                os.remove(filename);
                print("file deleted: " + filename)
                ret = '1'
            finally:
                pass
    return ret

@route('/queue/star/:name')
def queue_star_handler(name):
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename):
            os.rename(filename, filename + '.starred')
            ret = '1'
    return ret

@route('/queue/unstar/:name')
def queue_unstar_handler(name):
    ret = '0'
    filename = os.path.abspath(os.path.join(storage_dir(), name.strip('/\\')))
    if filename.startswith(storage_dir()):
        if os.path.exists(filename + '.starred'):
            os.rename(filename + '.starred', filename)
            ret = '1'
    return ret




@route('/')
@route('/index.html')
@route('/app.html')
def default_handler():
    return static_file('app.html', root=os.path.join(resources_dir(), 'frontend/original') )


@route('/stash_download', method='POST')
def stash_download():
    """Create a download file event from string."""
    filedata = request.forms.get('filedata')
    fp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    filename = fp.name
    with fp:
        fp.write(filedata)
        fp.close()
    print(filedata)
    print("file stashed: " + os.path.basename(filename))
    return os.path.basename(filename)

@route('/download/:filename/:dlname')
def download(filename, dlname):
    print("requesting: " + filename)
    return static_file(filename, root=tempfile.gettempdir(), download=dlname)


@route('/serial/:connect')
def serial_handler(connect):
    print('connect', connect)
    if connect == '1':
        # print 'js is asking to connect serial'
        if not SerialManager.is_connected():
            #try:
            SerialManager.connect()
            ret = 'Serial backend connected.<br>'
            print(ret)
            return ret
            #except serial.SerialException:
            #    SERIAL_PORT = None
            #    print "Failed to connect to serial."
            #    return ""
    elif connect == '0':
        # print 'js is asking to close serial'
        if SerialManager.is_connected():
            if SerialManager.close(): return "1"
            else: return ""
    elif connect == "2":
        # print 'js is asking if serial connected'
        if SerialManager.is_connected(): return "1"
        else: return ""
    else:
        print('ambigious connect request from js: ' + connect)
        return ""



@route('/status')
def get_status():
    status = copy.deepcopy(SerialManager.get_hardware_status())
    status['serial_connected'] = SerialManager.is_connected()
    status['lasaurapp_version'] = VERSION
    return json.dumps(status)


@route('/pause/:flag')
def set_pause(flag):
    # returns pause status
    if flag == '1':
        if SerialManager.set_pause(True):
            print("pausing ...")
            return '1'
        else:
            return '0'
    elif flag == '0':
        print("resuming ...")
        if SerialManager.set_pause(False):
            return '1'
        else:
            return '0'


@route('/flash_firmware')
@route('/flash_firmware/:firmware_file')
def flash_firmware_handler(firmware_file=FIRMWARE):
    ret.append('<h2>Flashing not supported by this backend!</h2>')
    return ''

@route('/build_firmware')
def build_firmware_handler():
    ret.append('<h2>Building not supported by this backend!</h2>')
    return ''

@route('/gcode', method='POST')
def job_submit_handler():
    job_data = request.forms.get('job_data')
    if job_data and SerialManager.is_connected():
        SerialManager.queue_gcode(job_data)
        return "__ok__"
    else:
        return "serial disconnected"


@route('/queue_pct_done')
def queue_pct_done_handler():
    return SerialManager.get_queue_percentage_done()


@route('/file_reader', method='POST')
def file_reader():
    """Parse SVG string."""
    filename = request.forms.get('filename')
    filedata = request.forms.get('filedata')
    dimensions = request.forms.get('dimensions')
    try:
        dimensions = json.loads(dimensions)
    except TypeError:
        dimensions = None
    # print "dims", dimensions[0], ":", dimensions[1]


    dpi_forced = None
    try:
        dpi_forced = float(request.forms.get('dpi'))
    except:
        pass

    optimize = True
    try:
        optimize = bool(int(request.forms.get('optimize')))
    except:
        pass

    if filename and filedata:
        print("You uploaded %s (%d bytes)." % (filename, len(filedata)))
        if filename[-4:] in ['.dxf', '.DXF']:
            res = read_dxf(filedata, TOLERANCE, optimize)
        elif filename[-4:] in ['.svg', '.SVG']:
            res = read_svg(filedata, dimensions, TOLERANCE, dpi_forced, optimize)
        elif filename[-4:] in ['.ngc', '.NGC']:
            res = read_ngc(filedata, TOLERANCE, optimize)
        else:
            print("error: unsupported file format")

        # print boundarys
        jsondata = json.dumps(res)
        # print "returning %d items as %d bytes." % (len(res['boundarys']), len(jsondata))
        return jsondata
    return "You missed a field."



# def check_user_credentials(username, password):
#     return username in allowed and allowed[username] == password
#
# @route('/login')
# def login():
#     username = request.forms.get('username')
#     password = request.forms.get('password')
#     if check_user_credentials(username, password):
#         response.set_cookie("account", username, secret=COOKIE_KEY)
#         return "Welcome %s! You are now logged in." % username
#     else:
#         return "Login failed."
#
# @route('/logout')
# def login():
#     username = request.forms.get('username')
#     password = request.forms.get('password')
#     if check_user_credentials(username, password):
#         response.delete_cookie("account", username, secret=COOKIE_KEY)
#         return "Welcome %s! You are now logged out." % username
#     else:
#         return "Already logged out."



### Setup Argument Parser
argparser = argparse.ArgumentParser(description='Run LasaurApp backend.', prog='lasaurapp')
argparser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION)
argparser.add_argument('-p', '--public', dest='host_on_all_interfaces', action='store_true',
                    default=False, help='bind to all network devices (default: bind to 127.0.0.1)')
argparser.add_argument('-d', '--debug', dest='debug', action='store_true',
                    default=False, help='print more verbose for debugging')
args = argparser.parse_args()



print("LasaurApp " + VERSION)

if __name__ == '__main__':
    if args.host_on_all_interfaces:
        run_with_callback('', NETWORK_PORT)
    else:
        run_with_callback('127.0.0.1', NETWORK_PORT)
