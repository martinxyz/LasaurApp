import os
import sys
import time
import ast
import struct
import serial
#import serial.tools.list_ports
from tornado.ioloop import IOLoop, PeriodicCallback

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
                assert value[0] == "'", line
                value = ast.literal_eval('b'+value)[0]
                yield name, value

markers_tx = {}
markers_rx = {}
for name, value in get_firmware_constants():
    prefix = name.split('_')[0]
    if prefix in ['CMD', 'PARAM']:
        markers_tx[value] = name
        globals()[name] = value
    elif prefix in ['INFO', 'STOPERROR', 'STATUS']:
        markers_rx[value] = name
        globals()[name] = value

class Driveboard:
    def __init__(self, port='/dev/ttyUSB0'):
        self.io_loop = IOLoop.current()
        self.serial_write_queue = bytearray()
        self.device = None
        self.port = port

        self.pdata = []

        self.firmbuf_used = 0
        self.firmbuf_queue = bytearray()

        # always request status (while connected) every 100ms
        self.last_status_request = 0.0
        self.last_status_report = 0.0
        self.status = {}
        self.next_status = {}
        polling_interval = 200 # milliseconds
        PeriodicCallback(self.status_timer_cb, polling_interval).start()

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
        self.serial_write_queue.clear()

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
            self.serial_write(b'')

    def serial_write(self, data):
        if not self.device:
            print('write ignored (device not open):', repr(data))
            return
        queue = self.serial_write_queue
        for b in data:
            # by protocol send twice
            queue.append(b)
            queue.append(b)
        if queue:
            n = self.device.write(queue)
            #print('tx', repr(queue[:n]))
            del queue[:n]
            if queue:
                print(len(queue), 'bytes still waiting in queue after tx')
                self.io_loop.update_handler(fd, IOLoop.READ | IOLoop.WRITE)
        else:
            self.io_loop.update_handler(fd, IOLoop.READ)

    def serial_read(self):
        data = self.device.read()
        #print('type', type(data))
        if not data:
            raise RuntimeError('no read data - maybe serial port was closed?')
        for byte in data:
            name = markers_rx.get(byte, repr(byte))
            if byte < 32:  # flow
                if byte == CMD_CHUNK_PROCESSED:
                    self.firmbuf_used -= TX_CHUNK_SIZE
                    if self.firmbuf_used < 0:
                        print("ERROR: firmware buffer tracking too low")
                elif byte == STATUS_END:
                    self.last_status_report = time.time()
                    for key in sorted(set(self.status).union(set(self.next_status))):
                        value1 = self.status.get(key)
                        value2 = self.next_status.get(key)
                        if value1 != value2:
                            print('Status change:', key, repr(value2))
                    self.status = self.next_status
                    self.next_status = {}
                    #print('status frame complete:', repr(self.status))
                else:
                    print('unhandled rx', repr(bytes([byte])), name)
            elif 31 < byte < 65:  # stop error markers
                self.next_status[name] = True
            elif 64 < byte < 91:  # info flags
                self.next_status[name.lower().replace('info_', '')] = True
            elif 96 < byte < 123:  # parameter
                if len(self.pdata) == 4:
                    value = (( (self.pdata[3]-128)*2097152
                             + (self.pdata[2]-128)*16384
                             + (self.pdata[1]-128)*128
                             + (self.pdata[0]-128))- 134217728)/1000.0
                else:
                    print('ERROR: not enough parameter data', name, len(self.pdata))
                self.pdata = []
                self.next_status[name] = value
            elif byte > 127:  # data
                if len(self.pdata) < 4:
                    self.pdata.append(byte)
                else:
                    print("ERROR: invalid data")
                    self.pdata = []
            else:
                assert False  # cannot be reached

    def send_command(self, cmd):
        if cmd < 32:
            # controls chars, handled directly in the serial ISR (not buffered)
            self.serial_write(bytes([cmd]))
        else:
            self.send_fwbuf(bytes([cmd]))

    def send_param(self, param, val):
        # num to be [-134217.728, 134217.727], [-2**27, 2**27-1]
        # three decimals are retained
        num = int(round(((val+134217.728)*1000)))
        data = struct.pack(
            'BBBBB',
            (num&127)+128,
            ((num&(127<<7))>>7)+128,
            ((num&(127<<14))>>14)+128,
            ((num&(127<<21))>>21)+128,
            buf.append(param))
        self.send_fwbuf(data)

    def send_fwbuf(self, data):
        self.firmbuf_queue += data
        available = FIRMBUF_SIZE - self.firmbuf_used
        if available > TX_CHUNK_SIZE and self.firmbuf_queue:
            out = self.firmbuf_queue[:available]
            del self.firmbuf_queue[:available]
            self.firmbuf_used += len(out)
            print('firmbuf_used', self.firmbuf_used, 'of', FIRMBUF_SIZE)
            self.serial_write(out)

    def status_timer_cb(self):
        if self.device:
            self.send_command(CMD_STATUS)
            self.last_status_request = time.time()

    # TODO:
    #### sending super commands (handled in serial rx interrupt)
    #if self.request_stop:
    #    self._send_char(CMD_STOP)
    #    self.request_stop = False
    #
    #if self.request_resume:
    #    self._send_char(CMD_RESUME)
    #    self.request_resume = False
    #    self.reset_status()
    #    self.request_status = 2  # super request

