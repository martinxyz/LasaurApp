import os
import sys
import time
import math
import json
import copy
import ast
import numpy
import serial
import serial.tools.list_ports
from tornado.ioloop import IOLoop

from config import conf

## firmware constants, need to match device firmware
## (maybe they should be reported by the firmware's superstatus)
TX_CHUNK_SIZE = 16 # number of bytes written to the device in one go
FIRMBUF_SIZE = 256
RASTER_BYTES_MAX = 60
PULSE_SECONDS = 31.875e-6 # see laser.c
MINIMUM_PULSE_TICKS = 3 # unit: PULSE_SECONDS
MAXIMUM_PULSE_TICKS = 127 # unit: PULSE_SECONDS
ACCELERATION = 1800000.0 # mm/min^2, divide by (60*60) to get mm/sec^2

# "import" firmware protocol constants

def get_firmware_constants():
    file_dir = os.path.dirname(__file__)
    for line in open(file_dir + '/../firmware/src/protocol.h'):
        if line.startswith('#define'):
            parts = line.split(maxsplit=2)
            if len(parts) == 3:
                define, name, value = parts
                value = ast.literal_eval(value)
                yield name, value

markers_tx = {}
markers_rx = {}
for name, value in get_firmware_constants():
    prefix = name.split('_')[0]
    if prefix in ['CMD', 'PARAM']:
        value = ord(value)
        markers_tx[value] = name
        globals()[name] = value
    elif prefix in ['INFO', 'STOPERROR', 'STATUS']:
        value = ord(value)
        markers_rx[value] = name
        globals()[name] = value


class Driveboard:
    def __init__(self, port='/dev/ttyUSB0'):
        self.io_loop = IOLoop.current()
        self.write_queue = bytearray()
        self.device = None
        self.port = port

        self.pdata = []

        self.firmbuf_used = 0

    def connect(self):
        if self.device is not None:
            return
        try:
            print('opening serial port', repr(conf['serial_port']), 'baudrate', conf['baudrate'])
            self.device = serial.Serial(conf['serial_port'], conf['baudrate'])
            self.device.timeout = 0
            self.device.write_timeout = 0
            self.device.nonblocking()
            self.io_loop.add_handler(self.device, self.serial_event, IOLoop.READ)
        except serial.SerialException as e:
            print(e)
            self.device = None
            return str(e)

    def disconnect(self):
        self.io_loop.remove_handler(self.device)
        self.device.close()
        self.device = None
        self.write_queue.clear()

    def is_connected(self):
        return bool(self.device)

    def serial_event(self, fd, events):
        if events & IOLoop.READ:
            try:
                self.serial_read()
            except serial.SerialException:
                self.disconnect()
                print('Error while reading - disconnecting. Exception follows:')
                raise
        if events & IOLoop.WRITE:
            self.serial_write_raw(b'')

    def serial_write_raw(self, data):
        if not self.device:
            print('write ignored (device not open):', repr(data))
            return
        queue = self.write_queue
        queue += data
        if queue:
            n = self.device.write(queue)
            print('tx', repr(queue[:n]))
            del queue[:n]
            if queue:
                print(len(queue), 'bytes still waiting in queue after tx')
                self.io_loop.update_handler(fd, IOLoop.READ | IOLoop.WRITE)
        else:
            self.io_loop.update_handler(fd, IOLoop.READ)

    def serial_read(self):
        for byte in self.device.read():
            name = markers_rx.get(byte, '')
            print('rx', repr(chr(byte)), name)
            if byte < 32:  # flow
                if byte == CMD_CHUNK_PROCESSED:
                    self.firmbuf_used -= TX_CHUNK_SIZE
                    if self.firmbuf_used < 0:
                        print("ERROR: firmware buffer tracking too low")
                elif byte == STATUS_END:
                    print('status frame complete')
            elif 31 < byte < 65:  # stop error markers
                print('stop error marker', byte)
            elif 64 < byte < 91:  # info flags
                print('info flag', name)
            elif 96 < byte < 123:  # parameter
                if len(self.pdata) == 4:
                    num = ((((self.pdata[3]-128)*2097152
                           + (self.pdata[2]-128)*16384
                           + (self.pdata[1]-128)*128
                           + (self.pdata[0]-128))- 134217728)/1000.0)
                    print(name, num)
                else:
                    print('ERROR: not enough parameter data', name, len(self.pdata))
                self.pdata = []
            elif byte > 127:  # data
                if len(self.pdata) < 4:
                    self.pdata.append(byte)
                else:
                    print("ERROR: invalid data")
                    self.pdata = []
            else:
                print('ERROR: invalid byte received:', repr(chr(byte)), name)

    def serial_write(self):
        ### sending super commands (handled in serial rx interrupt)
        if self.request_status == 1:
            self._send_char(CMD_STATUS)
            self.request_status = 0
        elif self.request_status == 2:
            self._send_char(CMD_SUPERSTATUS)
            self.request_status = 0

        if self.request_stop:
            self._send_char(CMD_STOP)
            self.request_stop = False

        if self.request_resume:
            self._send_char(CMD_RESUME)
            self.request_resume = False
            self.reset_status()
            self.request_status = 2  # super request

        ### send buffer chunk
        if self.tx_buffer and len(self.tx_buffer) > self.tx_pos:
            if not self._paused:
                if (FIRMBUF_SIZE - self.firmbuf_used) > TX_CHUNK_SIZE:
                    try:
                        # to_send = ''.join(islice(self.tx_buffer, 0, TX_CHUNK_SIZE))
                        to_send = self.tx_buffer[self.tx_pos:self.tx_pos+TX_CHUNK_SIZE]
                        expectedSent = len(to_send)
                        # by protocol duplicate every char
                        to_send_double = []
                        for c in to_send:
                            to_send_double.append(c)
                            to_send_double.append(c)
                        to_send = ''.join(to_send_double)
                        #
                        t_prewrite = time.time()
                        actuallySent = self.device.write(to_send)
                        if actuallySent != expectedSent*2:
                            print("ERROR: write did not complete")
                            assumedSent = 0
                        else:
                            assumedSent = expectedSent
                            self.firmbuf_used += assumedSent
                            if self.firmbuf_used > FIRMBUF_SIZE:
                                print("ERROR: firmware buffer tracking too high")
                        if time.time() - t_prewrite > 0.1:
                            print("WARN: write delay 1")
                    except serial.SerialTimeoutException:
                        assumedSent = 0
                        print("ERROR: writeTimeoutError 2")
                    # for i in range(assumedSent):
                    #     self.tx_buffer.popleft()
                    self.tx_pos += assumedSent
        else:
            if self.tx_buffer:  # job finished sending
                self.job_size = 0
                self.tx_buffer = []
                self.tx_pos = 0

