#!/usr/bin/env python3
import logging
import tornado.options
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from tornado import gen

import build
import flash

class FirmwareHandler(tornado.web.RequestHandler):
    """HTTP Build and flash API
    """
    def initialize(self, board, conf):
        self.board = board
        self.conf = conf
    def post(self, action):
        if action == 'build':
            try:
                firmware_name = "LasaurGrbl_from_src"
                build.build_firmware(firmware_name)
            except build.BuildFailed as e:
                self.write(str(e))
                self.set_status(500, 'Build Failed')
        elif action == 'flash' or action == 'flash_release':
            if action == 'flash':
                firmware_name = "LasaurGrbl_from_src"
            elif action == 'flash_release':
                firmware_name = "LasaurGrbl"
            try:
                self.board.disconnect('flashing new firmware')
                flash.flash_upload(self.conf['driveboard'], firmware_name)
                self.board.connect()
            except flash.FlashFailed as e:
                self.write(str(e))
                self.set_status(500, 'Flash Failed')
        elif action == 'reset':
            try:
                self.board.disconnect('reset requested')
                flash.reset_atmega(self.conf['driveboard'])
                self.board.connect()
            except flash.FlashFailed as e:
                self.write(str(e))
                self.set_status(500, 'Reset Failed')
        else:
            self.set_status(501, 'not implemented')

class StatusHandler(tornado.web.RequestHandler):
    """HTTP status requests
    """
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def initialize(self, board):
        self.board = board

    def get(self):
        self.write(self.board.get_status())

class StatusWebsocket(tornado.websocket.WebSocketHandler):
    """Websocket for status updates (to avoid HTTP GET polling)
    """
    clients = set()
    started = False

    def initialize(self, board):
        if not StatusWebsocket.started:
            def status_timer_cb():
                status = board.get_status()
                for client in StatusWebsocket.clients:
                    client.new_status(status)
            polling_interval = 200  # milliseconds
            PeriodicCallback(status_timer_cb, polling_interval).start()
            StatusWebsocket.started = True

    def open(self):
        StatusWebsocket.clients.add(self)

    def on_close(self):
        StatusWebsocket.clients.remove(self)

    def new_status(self, status):
        # we always send it (even if not changed) to allow the client
        # to detect the lack of messages with a simple timeout
        self.write_message(status)

    def check_origin(self, origin):
        return True  # anyone may listen to status changes

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
            )
        self.write(res)

class GcodeHandler(tornado.web.RequestHandler):
    def initialize(self, board):
        self.board = board

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")

    def post(self):
        content_type = self.request.headers.get('Content-Type')
        if not content_type.startswith('text'):
            raise tornado.web.HTTPError(400, 'gcode POST handler supports only text/plain content-type')
        gcode = self.request.body
        # TODO: stop at first gcode error, e.g. at '{' if posting json (also, if line is longer than 1000 chars?)
        for line in gcode.split(b'\n'):
            # FIMXE: should be coroutine and add:
            # yield gen.moment
            # -    status['gcode_error'] = SerialManager.pop_gcode_error()
            line = line.decode('utf-8', 'ignore').strip()  # FIXME: why bother decoding it? Just keep it bytes.
            if line:
                resp = self.board.gcode_line(line) + '\n'
                if resp.startswith('error:'):
                    logging.warning(resp[6:])
                # TODO: Not sure if this non-json response is useful for javascript.
                #       Should probably also return HTTP error if disconnected, etc.
                self.write(resp.encode('utf-8'))
