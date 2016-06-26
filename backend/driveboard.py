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

        self.disconnect_reason = None
        self.firmware_version = None

        # always request status (while connected) every 100ms
        self.last_status_request = 0.0
        self.last_status_report = 0.0
        self.status = {}
        self.next_status = {}
        polling_interval = 100  # milliseconds
        PeriodicCallback(self._status_timer_cb, polling_interval).start()

    def reset_protocol(self):
        self.serial_write_queue.clear()
        self.read_hist.clear()
        self.firmbuf_queue.clear()
        self.firmbuf_used = 0
        self.pdata = []
        self.firmware_version = None
        self.send_command('CMD_RESET_PROTOCOL')
        self.send_command('CMD_SUPERSTATUS')

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
            self.disconnect_reason = str(e)
            logging.error(e)
            self.device = None
            return str(e)

        self.reset_protocol()
        self.greeting_timeout = self.io_loop.call_later(2.0, self._on_greeting_timeout)
        self.disconnect_reason = None
        return ''

    def disconnect(self, reason):
        logging.error(reason)
        self.disconnect_reason = reason
        if self.device is None:
            return
        logging.info('disconnecting from serial port %r', self.serial_port)
        self.io_loop.remove_handler(self.device)
        self.device.close()
        self.device = None

    def is_connected(self):
        return bool(self.device)

    def get_disconnect_reason(self):
        return self.disconnect_reason or 'disconnected'

    def get_status(self):
        status = self.status.copy()
        status['CONNECTED'] = self.is_connected()
        status['FIRMWARE_VERSION'] = self.firmware_version

        status['QUEUE_FIRMBUF'] = self.firmbuf_used
        # We don't know the exact state of the firmware buffer because
        # we receive a confirmation only every TX_CHUNK_SIZE bytes. But
        # for GUI purpose a "percent" display should show zero when idle.
        used_for_sure = max(0, self.firmbuf_used - TX_CHUNK_SIZE)
        percent = 100.0 * float(used_for_sure) / (FIRMBUF_SIZE - TX_CHUNK_SIZE)
        status['QUEUE_FIRMBUF_PERCENT'] = percent
        status['QUEUE_BACKEND'] = len(self.firmbuf_queue) + len(self.serial_write_queue)

        report = 'ok'
        if not self.device:
            report = 'disconnected from serial port'
            if self.disconnect_reason:
                report += ' - ' + self.disconnect_reason
        elif self.last_status_report < time.time() - 0.5:
            report = 'last status report from firmware is too old'
        elif not self.status.get('STOPERROR_OK'):
            stop_errors = []
            for k in status:
                if k.startswith('STOPERROR'):
                    stop_errors.append(k)
            report = 'stopped - ' + ' '.join(stop_errors)
        status['REPORT'] = report

        return status

    def _serial_event(self, fd, events):
        if events & IOLoop.READ:
            try:
                self._serial_read()
            except serial.SerialException:
                self.disconnect('could not read from serial port')
                raise
        if events & IOLoop.WRITE:
            self._serial_write()

    def _serial_write(self, data=b''):
        if not self.device:
            logging.warning('write ignored (device closed)')
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
                        logging.error('firmware buffer tracking too low (%d)', self.firmbuf_used)
                elif byte == STATUS_END:
                    self.last_status_report = time.time()
                    #for key in sorted(set(self.status).union(set(self.next_status))):
                    #    value1 = self.status.get(key)
                    #    value2 = self.next_status.get(key)
                    #    if value1 != value2:
                    #        logging.info('Status change: %s %r', key, value2)
                    self.status = self.next_status
                    self.next_status = {}
                    if 'INFO_VERSION' in self.status:
                        self.firmware_version = self.status['INFO_VERSION'] / 100.0
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
            if cmd == CMD_RESUME:
                if self.status.get('STOPERROR_RX_BUFFER_OVERFLOW') or \
                  self.status.get('STOPERROR_TRANSMISSION_ERROR'):
                  # need to fix the buffer tracking first
                  self.reset_protocol()
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

        if available > 0 and self.firmbuf_queue:
            out = self.firmbuf_queue[:available]
            del self.firmbuf_queue[:available]
            self.firmbuf_used += len(out)
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
                if self.firmbuf_used != 0:
                    self.disconnect('Startup error, firmbuf_used should remain empty during startup!')
            else:
                self.disconnect('Got firmware startup greeting. Unexpected firmware reset!')
        else:
            self.disconnect('Got invalid firmware startup greeting: %r' % repr(value))

    def _on_greeting_timeout(self):
        self.greeting_timeout = None
        if self.read_hist.startswith(b'# LasaurGrbl '):
            self.disconnect('Old LasaurGrbl firmware detected. Please flash the new one.')
        elif self.last_status_report < time.time() - 0.5:
            self.disconnect('No firmware startup greeting and no response to status request. Bytes received: %r' % self.read_hist)
        else:
            logging.info('Got no startup greeting, but firmware is responding to status requests.')
            if self.firmware_version:
                logging.info('Firmware version: %s', self.firmware_version)
            else:
                self.disconnect('Firmware did not report its version! Incompatible firmware?')
