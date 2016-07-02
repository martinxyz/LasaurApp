"""
Connect (and send gcode) to the websocket of the new backend.
"""

import sys
import time

from tornado.tcpclient import TCPClient
from tornado import gen
from tornado.escape import json_decode
from tornado.ioloop import IOLoop

class SerialManagerClass:
    def __init__(self):
        self.gcode_tcp = None
        self.last_poll = 0.0
        self.status = {}
        self.reset_status()

    def reset_status(self):
        # just the basics
        self.status['ready'] = False
        self.status['serial'] = False

    def connect(self):
        if self.gcode_tcp is not None:
            return False
        io_loop = IOLoop.current()
        io_loop.spawn_callback(self.gcode_tcp_connect)

    @gen.coroutine
    def gcode_tcp_connect(self):
        self.reset_status()

        gcode_tcp = yield TCPClient().connect('localhost', 7777)
        greeting = yield gcode_tcp.read_until(b'\n')
        assert b'LasaurGrbl2' in greeting, repr(greeting)

        try:
            self.gcode_tcp = gcode_tcp
            while True:
                res = yield gcode_tcp.read_until(b'\n')
                if res is None:
                    print('gcode-tcp connection closed.')
                    break
                self.gcode_tcp_line(res.decode('ascii'))
        finally:
            self.gcode_tcp = None
            self.reset_status()
            gcode_tcp.close()

    def gcode_tcp_line(self, line):
        if line.startswith('status:'):
            self.process_status(json_decode(line[7:]))
        elif line.startswith('error:'):
            print(line)

    def close(self):
        if self.gcode_tcp:
            self.gcode_tcp.close()
            self.status['ready'] = False
            return True
        else:
            return False

    def is_connected(self):
        return bool(self.gcode_tcp)

    def get_hardware_status(self):
        if time.time() - self.last_poll > 0.1:
            # trigger a status report
            # will update for the next status request
            self.queue_gcode('?full')
            self.last_poll = time.time()
        return self.status

    def queue_gcode(self, gcode):
        if not gcode.endswith('\n'):
            gcode += '\n'
        if not self.gcode_tcp:
            return
        self.gcode_tcp.write(gcode.encode('ascii'))

    def get_queue_percentage_done(self):
        return str(self.get_hardware_status()['queue']['job_percent'])

    def set_pause(self, flag):
        #if self.is_queue_empty():
        #    return False
        if flag:
            self.queue_gcode('!pause')
            return True
        else:
            self.queue_gcode('!unpause')
            return False

    def process_status(self, status):
        self.status = status

# singelton
SerialManager = SerialManagerClass()
