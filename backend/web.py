#!/usr/bin/env python3
import logging
import tornado.options
import tornado.web
import tornado.websocket
import tornado.tcpserver
#from tornado.escape import json_encode, json_decode
from tornado.ioloop import IOLoop
from tornado import gen
import os.path

from tornado.options import define, options


class GcodeServer(tornado.tcpserver.TCPServer):
    def __init__(self, board, **args):
        self.board = board
        super(GcodeServer, self).__init__(**args)

    @gen.coroutine
    def handle_stream(self, stream, address):
        logging.info('incoming "gcode over tcp" connection from %r', address)
        try:
            stream.write((self.board.version + '\n').encode('utf-8'))
            while True:
                line = yield stream.read_until(b'\n')
                line = line.decode('utf-8', 'ignore').strip()
                if line:
                    resp = self.board.gcode_line(line) + '\n'
                    if resp.startswith('error:'):
                        logging.warning(resp[6:])
                    stream.write(resp.encode('utf-8'))
        except tornado.iostream.StreamClosedError:
            logging.info('closed "gcode over tcp" by client %r', address)

class FirmwareHandler(tornado.web.RequestHandler):
    def initialize(self, board):
        self.board = board
    def post(self, action):
        if action == 'flash':
            print('TODO: flash')
        else:
            self.set_status(501, 'not implemented')
            #self.send_error(501)

class ConfigHandler(tornado.web.RequestHandler):
    def initialize(self, board, conf):
        self.board = board
        self.conf = conf
    def get(self):
        c = self.conf
        res = dict(
            baudrate=c.get('driveboard', 'baudrate'),
            serial_port=c.get('driveboard', 'serial_port'),
            original_port=c.get('original', 'network_port'),
            nothing=c.get('driveboard', 'balsdkfj', fallback=None),
            )
        self.write(res)

class GcodeHandler(tornado.web.RequestHandler):
    def initialize(self, board):
        self.board = board

    def post(self):
        gcode = self.get_body_argument()
        print('gcode was posted: %r' % gcode)

class WSHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def initialize(self, board):
        self.board = board

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        logging.info('The port-gate is open!')
        WSHandler.clients.add(self)

    def on_close(self):
        logging.info('The port-gate is closed.')
        WSHandler.clients.remove(self)

    def on_message(self, message):
        logging.info("got message %r", message)
        for line in message.split('\n'):
            if line:
                self.on_gcode(line)

    def on_gcode(self, line):
        print('executing gcode: %r' % line)
        resp = self.board.gcode_line(line)
        if resp.startswith('error:'):
            logging.warning(resp)

    def check_origin(self, origin):
        # TODO: this is bad; we don't really want javascript from
        # random websites to use our machine?
        # In addition, we also should require authentication.
        return True
