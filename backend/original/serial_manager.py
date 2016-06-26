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

        self.tx_index = 0
        self.remoteXON = True

        # TX_CHUNK_SIZE - this is the number of bytes to be
        # written to the device in one go. It needs to match the device.
        self.TX_CHUNK_SIZE = 16
        self.RX_CHUNK_SIZE = 16
        self.nRequested = 0

        # used for calculating percentage done
        self.job_active = False

        # status flags
        self.status = {}
        self.last_poll = 0.0
        self.reset_status()

        self.LASAURGRBL_FIRST_STRING = "LasaurGrbl"

        self.ready_char = '\x12'
        self.request_ready_char = '\x14'
        self.last_request_ready = 0



    def reset_status(self):
        self.status = {
            'ready': False,  # turns True by querying status (TODO)
            'paused': False,  # this is also a control flag
            'power_off': False,
            'limit_hit': False,
            'serial_stop_request': False,
            'door_open': False,
            'chiller_off': False,
            'x': False,
            'y': False,
            'firmware_version': None,
            'error': None
        }

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
        print('got greeting', repr(greeting))
        assert(b'LasaurGrbl2' in greeting)

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


    def flush_input(self):
        if self.device:
            self.device.flushInput()

    def flush_output(self):
        if self.device:
            self.device.flushOutput()


    def queue_gcode(self, gcode):
        if not self.gcode_tcp:
            return
        lines = gcode.split('\n')
        for line in lines:
            line = line.strip()
            if line == '' or line[0] == '%':
                continue

            if not line.startswith('?'):  # not ready unless just a ?-query
                self.status['ready'] = False
            line += '\n'
            self.gcode_tcp.write(line.encode('ascii'))

        self.job_active = True

    def is_queue_empty(self):
        print('TODO: is_queue_empty')


    def get_queue_percentage_done(self):
        print('TODO: get_queue_percentage_done')
        #buflen = len(self.tx_buffer)
        #if buflen == 0:
        #    return ""
        #return str(100*self.tx_index/float(buflen))


    def set_pause(self, flag):
        # returns pause status
        if self.is_queue_empty():
            return False
        else:
            if flag:  # pause
                self.status['paused'] = True
                return True
            else:     # unpause
                self.status['paused'] = False
                return False


    def process_status(self, status):
        self.status['x'] = status['INFO_POS_X']
        self.status['y'] = status['INFO_POS_Y']
        self.status['serial_connected'] = status['CONNECTED']
        self.status['ready'] = status.get('INFO_IDLE_YES')
        if not status.get('STOPERROR_OK'):
            self.status['ready'] = False
        self.status['door_open'] = status.get('INFO_DOOR_OPEN')
        self.status['chiller_off'] = status.get('INFO_CHILLER_OFF')
        self.status['firmware_version'] = status.get('FIRMWARE_VERSION')
        report = status['REPORT']
        if report == 'ok':
            self.status['error'] = None
        else:
            self.status['error'] = report



# singelton
SerialManager = SerialManagerClass()
