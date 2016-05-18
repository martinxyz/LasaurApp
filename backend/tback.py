#!/usr/bin/env python3
import logging
import tornado.options
import tornado.web
import tornado.websocket
#from tornado.escape import json_encode, json_decode
from tornado.ioloop import IOLoop
import os.path
import subprocess
import atexit

from config import conf
import hardware_init
import driveboard

from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio

from tornado.options import define, options

define("port", default=conf['websocket_port'], help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        board = driveboard.Driveboard()
        board.connect()
        #self.board.serial_write_raw(b'aslfdkajsflaksjflask')
        handlers = [
            (r"/", MainHandler),
            (r"/ws", WSHandler, dict(board=board)),
            #(r"/status", StatusHandler, dict(board=board)),
            #(r"/serial/([0-9]+)", OldApiSerialHandler, dict(board=board)),
            (r"/(.*)", tornado.web.StaticFileHandler, {"path": "../frontend"}),

        ]
        settings = dict(
            # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",  #TODO: check if we need this (besides auth); requires html changes
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            #static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", messages=['foo', 'bar', 'baz'])

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
        logging.info("got message %r", message)
        #parsed = tornado.escape.json_decode(message)
        #print(parsed)

        parts = message.split(' ')
        command = parts[0]
        args = parts[1:]

        if command == 'list':
            res = {'SerialPorts': [{
                'Name': 'Lasersaur',
                'Friendly': 'Lasersaur',
                'Baudrate': [57600, 115200],
                #'AvailableBufferAlgorithms': ['lasersaur2'],
                'AvailableBufferAlgorithms': ['grbl', 'lasersaur2'],
                'IsOpen': False,
            }]}
            self.write_message(res)
        elif command == 'open':
            # TODO: should notify all browsers, not just the current one?
            port = args[0]
            error = None
            if port == 'Lasersaur':
                if not self.board.is_connected():
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
                    logging.info('executing gcode: %r', gcode)
                    self.board.gcode_line(gcode)

    def on_gcode(self, line):
        line = line.split(';')[0]  # gcode comment
        parts = line.strip()
        if not parts:
            return
        args = {}
        cmd = parts[0]
        for part in parts[1:]:
            letter = part[0]
            number = part[1:]
            args[letter] = number
        if cmd == '?':
            st = self.board.status
            # status report (per client)
            # https://github.com/grbl/grbl/wiki/Interfacing-with-Grbl
            #data = '<Idle,MPos:0.000,0.000,0.000,WPos:0.000,0.000,0.000>'
            data = '<Idle,MPos:0.000,0.000,0.000,WPos:0.000,0.000,0.000>'
            #data = '<asldfkasjfd>'
            self.write_message({'P': 'Lasersaur', 'D': data})
        if cmd in ('G0', 'G1'):
            print('should move to', args.get('X'), args.get('Y'), args.get('Z'))
        else:
            print('unknown command:', cmd)


    def check_origin(self, origin):
        # TODO: this is bad; we don't really want javascript from
        # random websites to use our machine?
        # In addition, we also should require authentication.
        return True

def start_old_backend(public=False, debug=True):
    original_backend_main = os.path.join(os.path.split(__file__)[0], 'original/app.py')
    cmd = ['python3', original_backend_main]
    if public: cmd.append('--public')
    if debug: cmd.append('--debug')
    print('starting original backend:', ' '.join(cmd))
    p = subprocess.Popen(cmd)
    def stop_old_backend():
        print('killing original backend')
        p.terminate()
    atexit.register(stop_old_backend)

def main():
    hardware_init.init()
    tornado.options.parse_command_line()
    io_loop = IOLoop.current()
    app = Application()
    start_old_backend()
    app.listen(port=conf['websocket_port'], address=conf['network_host'])
    app.listen(port=conf['network_port'], address=conf['network_host'])
    io_loop.start()

if __name__ == "__main__":
    main()
