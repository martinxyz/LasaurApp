#!/usr/bin/env python3
import logging
import tornado.options
import tornado.web
import tornado.websocket
from tornado.ioloop import IOLoop
import os.path
import subprocess
import atexit
import argparse
import configparser

import hardware_init
import driveboard

class Application(tornado.web.Application):
    def __init__(self, conf):
        board = driveboard.Driveboard(
            conf['driveboard']['serial_port'],
            conf['driveboard'].getint('baudrate'))
        board.connect()
        # self.board.serial_write_raw(b'aslfdkajsflaksjflask')
        handlers = [
            (r"/ws", WSHandler, dict(board=board)),
            # (r"/status", StatusHandler, dict(board=board)),
            (r"/(build|flash|reset)", FirmwareHandler, dict(board=board)),
            (r"/config", ConfigHandler),
            # (r"/serial/([0-9]+)", OldApiSerialHandler, dict(board=board)),
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
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            # static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=conf['backend'].getboolean('debug', False),
            # autoreload=False,
        )
        super(Application, self).__init__(handlers, **settings)


class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(conf)


class FirmwareHandler(tornado.web.RequestHandler):
    def get(self):
        print('got it')
        return


class WSHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def initialize(self, board):
        self.board = board

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        logging.info('The gate is open!')
        WSHandler.clients.add(self)

    def on_close(self):
        logging.info('The gate is closed.')
        WSHandler.clients.remove(self)

    def on_message(self, message):
        # logging.info("got message %r", message)
        # parsed = tornado.escape.json_decode(message)
        # print(parsed)

        parts = message.split(' ')
        command = parts[0]
        args = parts[1:]

        if command == 'list':
            res = {'SerialPorts': [{
                'Name': 'Lasersaur',
                'Friendly': 'Lasersaur',
                'Baudrate': [57600, 115200],
                # 'AvailableBufferAlgorithms': ['lasersaur2'],
                'AvailableBufferAlgorithms': ['grbl', 'lasersaur2'],
                'IsOpen': False,
            }]}
            self.write_message(res)
        elif command == 'open':
            # TODO: should notify all browsers, not just the current one?
            port = args[0]
            error = None
            if port == 'Lasersaur':
                error = self.board.connect()
            else:
                error = 'Port must be "Lasersaur"'
            if not error:
                assert self.board.is_connected()
                self.write_message({'Cmd': 'Open', 'Port': port})
                # emulate firmware greeting
                self.write_message({'P': 'Lasersaur', 'D': 'ok C: X:'})
            else:
                self.write_message({'Cmd': 'OpenFail', 'Port': port, 'Desc': error})
        elif command == 'close':
            # TODO: should notify all browsers, not just the current one?
            port = args[0]
            if port == 'Lasersaur':
                self.write_message({'Cmd': 'Close', 'Port': port})
        elif command == 'send':
            if args[0] == 'Lasersaur':
                gcode = ' '.join(args[1:])
                # TODO: move this into own module (reusing 'parts' local var)
                for line in gcode.split('\n'):
                    if line:
                        self.on_gcode(line)
        else:
            logging.warning("got unknown message %r", message)

    def on_gcode(self, line):
        if not self.board.is_connected:
            return
        line = line.split(';')[0].strip()  # gcode comment
        if line == '?':  # status
            st = self.board.status
            # status report (per client)
            # https://github.com/grbl/grbl/wiki/Interfacing-with-Grbl
            # data = '<Idle,MPos:0.000,0.000,0.000,WPos:0.000,0.000,0.000>'
            data = '<Idle,MPos:%.3f,%.3f,%.3f,WPos:0.000,0.000,0.000>' % \
                   (st['INFO_POS_X'], st['INFO_POS_Y'], st['INFO_POS_Z'])
            self.write_message({'P': 'Lasersaur', 'D': data})
        else:
            print('executing gcode: %r' % line)
            self.board.gcode_line(line)

    def check_origin(self, origin):
        # TODO: this is bad; we don't really want javascript from
        # random websites to use our machine?
        # In addition, we also should require authentication.
        return True


def start_old_backend(conf):
    orig_app = os.path.join(os.path.split(__file__)[0],
                            'original', 'original_app.py')
    cmd = ['python3', orig_app]
    if conf.getboolean('public', False):
        cmd.append('--public')
    if conf.getboolean('debug', False):
        cmd.append('--debug')
    print('starting original backend:', ' '.join(cmd))
    p = subprocess.Popen(cmd)

    def stop_old_backend():
        print('killing original backend')
        p.terminate()
    atexit.register(stop_old_backend)


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
    app = Application(conf)

    public = conf.getboolean('backend', 'public')

    start_old_backend(conf['backend'])

    port = conf.getint('backend', 'network_port')
    if public:
        addr = ''
    else:
        addr = '127.0.0.1'

    app.listen(port=port, address=addr)
    app.listen(port=7777, address=addr)
    io_loop.start()

if __name__ == "__main__":
    main()
