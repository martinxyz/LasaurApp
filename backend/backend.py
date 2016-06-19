#!/usr/bin/env python3
import logging
import tornado.options
import tornado.web
from tornado.ioloop import IOLoop
import os.path
import subprocess
import atexit
import argparse
import configparser

import hardware_init
from gcode import DriveboardGcode
import web

class Application(tornado.web.Application):
    def __init__(self, conf, board):
        handlers = [
            (r"/ws", web.WSHandler, dict(board=board)),
            (r"/gcode", web.GcodeHandler, dict(board=board)),
            # (r"/status", web.StatusHandler, dict(board=board)),
            (r"/(build|flash|reset)", web.FirmwareHandler, dict(board=board)),
            (r"/config", web.ConfigHandler),
            (r"/raster/(.*)", tornado.web.StaticFileHandler, {
                "path": "../frontend/raster",
                "default_filename": "index.html"
            }),
            (r"/(.*)", tornado.web.StaticFileHandler, {
                "path": "../frontend/admin",
                "default_filename": "index.html"
            }),
        ]
        settings = dict(
            # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",  #TODO: check if we need this (besides auth); requires html changes
            xsrf_cookies=True,
            debug=conf['backend'].getboolean('debug', False),
            autoreload=False,  # avid multiple calls to start_old_backend()
        )
        super(Application, self).__init__(handlers, **settings)

def start_old_backend(conf):
    orig_app = os.path.join(os.path.split(__file__)[0],
                            'original', 'original_app.py')
    cmd = ['python3', orig_app]
    if conf.getboolean('public', False):
        cmd.append('--public')
    if conf.getboolean('debug', False):
        cmd.append('--debug')
    cmd.extend(['--network-port', str(conf.getint('network_port', 4444))])
    logging.info('starting original backend:' + ' '.join(cmd))
    p = subprocess.Popen(cmd)
    atexit.register(p.terminate)


def main():
    parser = argparse.ArgumentParser(description='Lasersaur backend server')
    parser.add_argument('configfile', metavar='configfile.ini',
                        help='port and gpio config file (e.g. beaglebone.ini)')
    args = parser.parse_args()
    conf = configparser.ConfigParser()
    conf.read(args.configfile)

    hardware_init.init(conf['driveboard']['board'])

    tornado.options.parse_command_line()
    io_loop = IOLoop.current()

    board = DriveboardGcode(
        conf['driveboard']['serial_port'],
        conf['driveboard'].getint('baudrate'))
    board.connect()
    # self.board.serial_write_raw(b'aslfdkajsflaksjflask')

    app = Application(conf, board)

    start_old_backend(conf['original'])

    public = conf.getboolean('backend', 'public')
    port = conf.getint('backend', 'network_port')
    if public:
        addr = ''
    else:
        addr = '127.0.0.1'
    app.listen(port, addr)
    # app.listen(7777, addr)

    gcode_tcp = web.GcodeServer(board)
    gcode_tcp.listen(7777, '127.0.0.1')

    io_loop.start()

if __name__ == "__main__":
    main()
