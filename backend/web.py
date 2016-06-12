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
                    stream.write(resp.encode('utf-8'))
        except tornado.iostream.StreamClosedError:
            logging.info('closed "gcode over tcp" by client %r', address)

class FirmwareHandler(tornado.web.RequestHandler):
    def get(self):
        print('got it fwhandler')

class ConfigHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(conf)

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
        if not self.board.is_connected:
            return
        line = line.split(';')[0].strip()  # gcode comment
        if line == '?':  # status polling
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

def main():
    tornado.options.parse_command_line()
    hardware_init.init(options.board)
    io_loop = IOLoop.current()
    app = Application()
    app.listen(port=options.port, address=options.addr)
    io_loop.start()

if __name__ == "__main__":
    main()
