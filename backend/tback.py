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


markers_tx = {
    "\x01": "CMD_STOP",
    "\x02": "CMD_RESUME",
    "\x03": "CMD_STATUS",
    "\x04": "CMD_SUPERSTATUS",
    "\x05": "CMD_CHUNK_PROCESSED",
    "\x09": "STATUS_END",

    "A": "CMD_NONE",
    "B": "CMD_LINE",
    "C": "CMD_DWELL",

    "E": "CMD_REF_RELATIVE",
    "F": "CMD_REF_ABSOLUTE",

    "G": "CMD_HOMING",

    "H": "CMD_SET_OFFSET_TABLE",
    "I": "CMD_SET_OFFSET_CUSTOM",
    "J": "CMD_SEL_OFFSET_TABLE",
    "K": "CMD_SEL_OFFSET_CUSTOM",

    "L": "CMD_AIR_ENABLE",
    "M": "CMD_AIR_DISABLE",
    "N": "CMD_AUX1_ENABLE",
    "O": "CMD_AUX1_DISABLE",
    "P": "CMD_AUX2_ENABLE",
    "Q": "CMD_AUX2_DISABLE",

    "x": "PARAM_TARGET_X",
    "y": "PARAM_TARGET_Y",
    "z": "PARAM_TARGET_Z",
    "f": "PARAM_FEEDRATE",
    "p": "PARAM_PULSE_FREQUENCY",
    "d": "PARAM_PULSE_DURATION",
    "r": "PARAM_RASTER_BYTES",
    "h": "PARAM_OFFTABLE_X",
    "i": "PARAM_OFFTABLE_Y",
    "j": "PARAM_OFFTABLE_Z",
    "k": "PARAM_OFFCUSTOM_X",
    "l": "PARAM_OFFCUSTOM_Y",
    "m": "PARAM_OFFCUSTOM_Z",
}

markers_rx = {
    # status: error flags
    '!': "ERROR_SERIAL_STOP_REQUEST",
    '"': "ERROR_RX_BUFFER_OVERFLOW",

    '$': "ERROR_LIMIT_HIT_X1",
    '%': "ERROR_LIMIT_HIT_X2",
    '&': "ERROR_LIMIT_HIT_Y1",
    '*': "ERROR_LIMIT_HIT_Y2",
    '+': "ERROR_LIMIT_HIT_Z1",
    '-': "ERROR_LIMIT_HIT_Z2",

    '#': "ERROR_INVALID_MARKER",
    ':': "ERROR_INVALID_DATA",
    '<': "ERROR_INVALID_COMMAND",
    '>': "ERROR_INVALID_PARAMETER",
    "(": "ERROR_VALUE_OUT_OF_RANGE",
    '=': "ERROR_TRANSMISSION_ERROR",
    ',': "ERROR_USART_DATA_OVERRUN",

    # status: info flags
    'A': "INFO_IDLE_YES",
    'B': "INFO_DOOR_OPEN",
    'C': "INFO_CHILLER_OFF",

    # status: info params
    'x': "INFO_POS_X",
    'y': "INFO_POS_Y",
    'z': "INFO_POS_Z",
    'v': "INFO_VERSION",
    'w': "INFO_BUFFER_UNDERRUN",
    'u': "INFO_STACK_CLEARANCE",
    't': "INFO_DELAYED_MICROSTEPS",

    '~': "INFO_HELLO",

    'a': "INFO_OFFCUSTOM_X",
    'b': "INFO_OFFCUSTOM_Y",
    'c': "INFO_OFFCUSTOM_Z",
    # 'd': "INFO_TARGET_X",
    # 'e': "INFO_TARGET_Y",
    # 'f': "INFO_TARGET_Z",
    'g': "INFO_FEEDRATE",
    'h': "INFO_PULSE_FREQUENCY",
    'i': "INFO_PULSE_DURATION",
}

# create a global constant for each of the names above
for char, name in list(markers_tx.items()):
    globals()[name] = char
for char, name in list(markers_rx.items()):
    globals()[name] = char

## more firmware constants, they need wo match device firmware
TX_CHUNK_SIZE = 16 # number of bytes written to the device in one go
RX_CHUNK_SIZE = 32
FIRMBUF_SIZE = 256
RASTER_BYTES_MAX = 60

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
            (r"/status", StatusHandler, dict(board=board)),
            (r"/serial/([0-9]+)", OldApiSerialHandler, dict(board=board)),
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

class StatusHandler(tornado.web.RequestHandler):
    def initialize(self, board):
        self.board = board

    def get(self):
        status = {
            'ready': self.board.is_connected(),  # turns True by querying status
            'paused': False,  # this is also a control flag
            'buffer_overflow': False,
            'transmission_error': False,
            'bad_number_format_error': False,
            'expected_command_letter_error': False,
            'unsupported_statement_error': False,
            'power_off': False,
            'limit_hit': False,
            'serial_stop_request': False,
            'door_open': False,
            'chiller_off': False,
            'x': False,
            'y': False,
            'firmware_version': None,
            'serial_connected': self.board.is_connected(),
            'lasaurapp_version': "14.11b",
        }
        #import time
        #status['serial_connected'] = bool((time.time() % 30) < 5)
        self.write(status)
        #self.render("index.html", messages=['foo', 'bar', 'baz'])

class OldApiSerialHandler(tornado.web.RequestHandler):
    def initialize(self, board):
        self.board = board

    def get(self, connect):
        if connect == '0':
            if self.board.is_connected():
                self.board.disconnect()
                self.write('1')
        elif connect == '1':
            if not self.board.is_connected():
                self.board.connect()
                if self.board.is_connected():
                    self.write('1')
        else:
            if self.board.is_connected():
                self.write('1')

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
                logging.info('should send: %r', gcode)
                # TODO: move this into own module (reusing 'parts' local var)
                for line in gcode.split('\n'):
                    parts = line.strip().split()
                    if not parts:
                        continue
                    args = {}
                    cmd = parts[0]
                    for part in parts[1:]:
                        letter = part[0]
                        number = part[1:]
                        args[letter] = number
                    if cmd in ('G0', 'G1'):
                        print('should move to', args.get('X'), args.get('Y'), args.get('Z'))
                    else:
                        print('unknown command:', cmd)

    def check_origin(self, origin):
        # TODO: this is bad; we don't really want javascript from
        # random websites to use our machine?
        # In addition, we also should require authentication.
        return True

def start_old_backend(public=False, debug=False):
    cmd = ['python', 'original/app.py']
    if public: cmd.append('--public')
    if debug: cmd.append('--debug')
    p = subprocess.Popen(cmd)
    def stop_old_backend():
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
