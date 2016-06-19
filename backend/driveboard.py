import os
import sys
import time
import ast
import struct
import serial
import logging
#import serial.tools.list_ports
from tornado.ioloop import IOLoop, PeriodicCallback

## firmware constants, need to match device firmware
## (maybe they should be reported by the firmware's superstatus)
TX_CHUNK_SIZE = 16 # number of bytes written to the device in one go
FIRMBUF_SIZE = 255-1 # the firmware sacrifices one byte to distinguish full from empty
RASTER_BYTES_MAX = 60
PULSE_SECONDS = 31.875e-6 # see laser.c
MINIMUM_PULSE_TICKS = 3 # unit: PULSE_SECONDS
MAXIMUM_PULSE_TICKS = 127 # unit: PULSE_SECONDS
ACCELERATION = 1800000.0 # mm/min^2, divide by (60*60) to get mm/sec^2

# "import" firmware protocol constants
markers_tx = {}
markers_rx = {}
name_to_marker = {}
def import_firmware_constants():
    def parse_headerfile():
        file_dir = os.path.dirname(__file__)
        for line in open(file_dir + '/../firmware/src/protocol.h'):
            if line.startswith('#define'):
                parts = line.split(maxsplit=2)
                if len(parts) == 3:
                    define, name, value = parts
                    assert value[0] == "'", line
                    value = ast.literal_eval('b'+value)[0]
                    yield name, value

    for name, value in parse_headerfile():
        prefix = name.split('_')[0]
        if prefix in ['CMD', 'PARAM']:
            markers_tx[value] = name
            name_to_marker[name] = value
        elif prefix in ['INFO', 'STOPERROR', 'STATUS']:
            markers_rx[value] = name
            name_to_marker[name] = value
    globals().update(name_to_marker)

import_firmware_constants()


class Driveboard:
    def __init__(self, serial_port, baudrate):
        self.serial_port = serial_port
        self.baudrate = baudrate

        self.io_loop = IOLoop.current()
        self.serial_write_queue = bytearray()
        self.device = None

        self.read_hist = bytearray()
        self.pdata = []

        self.firmbuf_used = 0
        self.firmbuf_queue = bytearray()

        # always request status (while connected) every 100ms
        self.last_status_request = 0.0
        self.last_status_report = 0.0
        self.status = {}
        self.next_status = {}
        polling_interval = 100  # milliseconds
        PeriodicCallback(self._status_timer_cb, polling_interval).start()

    def connect(self):
        if self.device is not None:
            return ''
        try:
            logging.info('opening serial port %r baudrate %s', self.serial_port, self.baudrate)
            self.device = serial.Serial(self.serial_port, self.baudrate)
            self.device.timeout = 0
            self.device.write_timeout = 0
            self.device.nonblocking()
            self.protocol_errors = 0
            self.io_loop.add_handler(self.device, self._serial_event, IOLoop.READ)
        except serial.SerialException as e:
            logging.error(e)
            self.device = None
            return str(e)

        self.greeting_timeout = self.io_loop.call_later(2.0, self._on_greeting_timeout)
        return ''

    def disconnect(self):
        logging.info('disconnecting from serial port %r', self.serial_port)
        self.io_loop.remove_handler(self.device)
        self.device.close()
        self.device = None
        self.serial_write_queue.clear()

    def is_connected(self):
        return bool(self.device)

    def get_status(self):
        status = self.status.copy()
        status['QUEUE_FIRMBUF'] = self.firmbuf_used
        # We don't know the exact state of the firmware buffer because
        # we receive a confirmation only every TX_CHUNK_SIZE bytes. But
        # for GUI purpose a "percent" display should show zero when idle.
        used_for_sure = max(0, self.firmbuf_used - TX_CHUNK_SIZE)
        percent = 100.0 * float(used_for_sure) / (FIRMBUF_SIZE - TX_CHUNK_SIZE)
        status['QUEUE_FIRMBUF_PERCENT'] = percent
        status['QUEUE_BACKEND'] = len(self.firmbuf_queue) + len(self.serial_write_queue)
        return status

    def _serial_event(self, fd, events):
        if events & IOLoop.READ:
            try:
                self._serial_read()
            except serial.SerialException:
                self.disconnect()
                logging.error('Error while reading - disconnecting. Exception follows:')
                raise
        if events & IOLoop.WRITE:
            self._serial_write()

    def _serial_write(self, data=b''):
        if not self.device:
            logging.error('write ignored (device not open): %r', data)
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
                # usually never reached (because fw_buffer < serial_buffer)
                #logging.warning('%d bytes still waiting in queue after tx', len(queue))
                self.io_loop.update_handler(self.device, IOLoop.READ | IOLoop.WRITE)
        else:
            self.io_loop.update_handler(self.device, IOLoop.READ)

    def _serial_read(self):
        data = self.device.read(2000)
        if not data:
            raise RuntimeError('no read data - maybe serial port was closed?')

        # for error diagnostics
        self.read_hist.extend(data)
        del self.read_hist[:-80]
        print_hist = False

        for byte in data:
            name = markers_rx.get(byte, repr(byte))
            if byte < 32:  # flow
                if byte == CMD_CHUNK_PROCESSED:
                    self.firmbuf_used -= TX_CHUNK_SIZE
                    #logging.debug('chunk processed, firmbuf_used %d/%d', self.firmbuf_used, FIRMBUF_SIZE)
                    self._send_fwbuf(b'')
                    if self.firmbuf_used < 0:
                        #logging.debug('firmware buffer tracking too low (%d), trying to recover', self.firmbuf_used)
                        self.firmbuf_used += 1  # slow (but safe) recovery
                elif byte == STATUS_END:
                    self.last_status_report = time.time()
                    for key in sorted(set(self.status).union(set(self.next_status))):
                        value1 = self.status.get(key)
                        value2 = self.next_status.get(key)
                        if value1 != value2:
                            logging.info('Status change: %s %r', key, value2)
                    self.status = self.next_status
                    self.next_status = {}
                else:
                    logging.warning('unhandled rx %r %s', bytes([byte]), name)
            elif 31 < byte < 65:  # stop error markers
                self.next_status[name] = True
            elif 64 < byte < 91:  # info flags
                self.next_status[name] = True
            elif 96 < byte < 123:  # parameter
                if len(self.pdata) == 4:
                    value = (( (self.pdata[3]-128)*2097152
                             + (self.pdata[2]-128)*16384
                             + (self.pdata[1]-128)*128
                             + (self.pdata[0]-128))- 134217728)/1000.0
                    self.pdata = []
                    if name == 'INFO_STARTUP_GREETING':
                        self._on_startup_greeting(value)
                    else:
                        self.next_status[name] = value
                else:
                    logging.error('not enough parameter data %s %d', name, len(self.pdata))
                    print_hist = True
            elif byte > 127:  # data
                if len(self.pdata) < 4:
                    self.pdata.append(byte)
                else:
                    logging.error("invalid data (rx history %s)")
                    self.pdata = []
                    print_hist = True
            else:
                logging.fatal('received invalid byte %d (firmware should never send this byte) (rx history %s)', byte, self.read_hist)
                print_hist = True

        if print_hist:
            hist = self.read_hist.decode('unicode-escape')
            logging.error('Last 80 bytes from firmware: %r', hist)

    def send_command(self, cmd):
        cmd = name_to_marker[cmd]
        if cmd < 32:
            # controls chars, handled directly in the serial ISR (not buffered)
            self._serial_write(bytes([cmd]))
        else:
            self._send_fwbuf(bytes([cmd]))

    def send_param(self, param, val):
        param = name_to_marker[param]
        # num to be [-134217.728, 134217.727], [-2**27, 2**27-1]
        # three decimals are retained
        num = int(round(((val+134217.728)*1000)))
        data = struct.pack(
            'BBBBB',
            (num&127)+128,
            ((num&(127<<7))>>7)+128,
            ((num&(127<<14))>>14)+128,
            ((num&(127<<21))>>21)+128,
            param)
        self._send_fwbuf(data)

    def _send_fwbuf(self, data=b''):
        self.firmbuf_queue += data
        available = FIRMBUF_SIZE - self.firmbuf_used
        # FIXME: why have I written the second one first? First one looks correct.
        #        verify that eve
        if available > 0 and self.firmbuf_queue:
        #if available > TX_CHUNK_SIZE and self.firmbuf_queue:
            out = self.firmbuf_queue[:available]
            del self.firmbuf_queue[:available]
            self.firmbuf_used += len(out)
            #logging.debug('firmbuf_used %d/%d', self.firmbuf_used, FIRMBUF_SIZE)
            self._serial_write(out)

    def _status_timer_cb(self):
        if self.device:
            self.send_command('CMD_STATUS')
            self.last_status_request = time.time()

    def _on_startup_greeting(self, value):
        if abs(value - 123.456) < 0.001:
            if self.greeting_timeout is not None:
                self.io_loop.remove_timeout(self.greeting_timeout)
                self.greeting_timeout = None
                logging.info('got firmware startup greeting')
            else:
                logging.error('got firmware startup greeting; unexpected firmware reset! Disconnecting.')
                self.disconnect()
            self.firmbuf_used = 0
        else:
            logging.warning('invalid firmware startup greeting: %r', repr(value))

    def _on_greeting_timeout(self):
        logging.error('No firmware greeting!')
        logging.error('Last 80 bytes from firmware: %r', self.read_hist)

        if self.read_hist.startswith(b'# LasaurGrbl '):
            logging.error('This is the old lasersaur firmware. Please flash the new one.')
            self.disconnect()
        elif self.last_status_report < time.time() - 0.5:
            logging.error('Also, there was no response to our status requests.')
            self.disconnect()
        else:
            logging.error('Firmware is responding to status requests.')
            logging.error('Not sure if the firmware is in a clean state. Buffer tracking may need recovery.')

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

