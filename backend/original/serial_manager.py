
import os
import sys
import time
from collections import deque


class SerialManagerClass:

    def __init__(self):
        self.device = None

        self.rx_buffer = ""
        self.tx_buffer = ""
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
        self.reset_status()

        self.LASAURGRBL_FIRST_STRING = "LasaurGrbl"

        self.ready_char = '\x12'
        self.request_ready_char = '\x14'
        self.last_request_ready = 0



    def reset_status(self):
        self.status = {
            'ready': True,  # turns True by querying status
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
            'firmware_version': None
        }



    def connect(self):
        self.rx_buffer = ""
        self.tx_buffer = ""
        self.tx_index = 0
        self.remoteXON = True
        self.reset_status()

        print 'TODO: serial connect'
        print 'self.device = serial.Serial(port, baudrate, timeout=0, writeTimeout=1)'

        self.device = True


    def close(self):
        if self.device:
            try:
                self.device.flushOutput()
                self.device.flushInput()
                self.device.close()
                self.device = None
            except:
                self.device = None
            self.status['ready'] = False
            return True
        else:
            return False

    def is_connected(self):
        return bool(self.device)

    def get_hardware_status(self):
        if self.is_queue_empty():
            # trigger a status report
            # will update for the next status request
            self.queue_gcode('?')
        return self.status


    def flush_input(self):
        if self.device:
            self.device.flushInput()

    def flush_output(self):
        if self.device:
            self.device.flushOutput()


    def queue_gcode(self, gcode):
        lines = gcode.split('\n')
        print "Adding to queue %s lines" % len(lines)
        job_list = []
        for line in lines:
            print "Adding line %r" % repr(line)
            line = line.strip()
            if line == '' or line[0] == '%':
                continue

            if line[0] == '!':
                self.cancel_queue()
                self.reset_status()
                job_list.append('!')
            else:
                if line != '?':  # not ready unless just a ?-query
                    self.status['ready'] = False
                job_list.append(line)

        gcode_processed = '\n'.join(job_list) + '\n'
        self.tx_buffer += gcode_processed
        print 'queueing', repr(gcode_processed)
        self.job_active = True


    def cancel_queue(self):
        self.tx_buffer = ""
        self.tx_index = 0
        self.job_active = False


    def is_queue_empty(self):
        return self.tx_index >= len(self.tx_buffer)


    def get_queue_percentage_done(self):
        buflen = len(self.tx_buffer)
        if buflen == 0:
            return ""
        return str(100*self.tx_index/float(buflen))


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


    def send_queue_as_ready(self):
        """Continuously call this to keep processing queue."""
        return
        if self.device and not self.status['paused']:
            try:
                ### receiving
                chars = self.device.read(self.RX_CHUNK_SIZE)
                if len(chars) > 0:
                    ## check for data request
                    if self.ready_char in chars:
                        # print "=========================== READY"
                        self.nRequested = self.TX_CHUNK_SIZE
                        #remove control chars
                        chars = chars.replace(self.ready_char, "")
                    ## assemble lines
                    self.rx_buffer += chars
                    while(1):  # process all lines in buffer
                        posNewline = self.rx_buffer.find('\n')
                        if posNewline == -1:
                            break  # no more complete lines
                        else:  # we got a line
                            line = self.rx_buffer[:posNewline]
                            self.rx_buffer = self.rx_buffer[posNewline+1:]
                        self.process_status_line(line)
                else:
                    if self.nRequested == 0:
                        time.sleep(0.001)  # no rx/tx, rest a bit

                ### sending
                if self.tx_index < len(self.tx_buffer):
                    if self.nRequested > 0:
                        try:
                            t_prewrite = time.time()
                            actuallySent = self.device.write(
                                self.tx_buffer[self.tx_index:self.tx_index+self.nRequested])
                            if time.time()-t_prewrite > 0.02:
                                sys.stdout.write("WARN: write delay 1\n")
                                sys.stdout.flush()
                        except serial.SerialTimeoutException:
                            # skip, report
                            actuallySent = 0  # assume nothing has been sent
                            sys.stdout.write("\nsend_queue_as_ready: writeTimeoutError\n")
                            sys.stdout.flush()
                        self.tx_index += actuallySent
                        self.nRequested -= actuallySent
                        if self.nRequested <= 0:
                            self.last_request_ready = 0  # make sure to request ready
                    elif self.tx_buffer[self.tx_index] in ['!', '~']:  # send control chars no matter what
                        try:
                            t_prewrite = time.time()
                            actuallySent = self.device.write(self.tx_buffer[self.tx_index])
                            if time.time()-t_prewrite > 0.02:
                                sys.stdout.write("WARN: write delay 2\n")
                                sys.stdout.flush()
                        except serial.SerialTimeoutException:
                            actuallySent = 0  # assume nothing has been sent
                            sys.stdout.write("\nsend_queue_as_ready: writeTimeoutError\n")
                            sys.stdout.flush()
                        self.tx_index += actuallySent
                    else:
                        if (time.time()-self.last_request_ready) > 2.0:
                            # ask to send a ready byte
                            # only ask for this when sending is on hold
                            # only ask once (and after a big time out)
                            # print "=========================== REQUEST READY"
                            try:
                                t_prewrite = time.time()
                                actuallySent = self.device.write(self.request_ready_char)
                                if time.time()-t_prewrite > 0.02:
                                    sys.stdout.write("WARN: write delay 3\n")
                                    sys.stdout.flush()
                            except serial.SerialTimeoutException:
                                # skip, report
                                actuallySent = self.nRequested  # pyserial does not report this sufficiently
                                sys.stdout.write("\nsend_queue_as_ready: writeTimeoutError, on ready request\n")
                                sys.stdout.flush()
                            if actuallySent == 1:
                                self.last_request_ready = time.time()

                else:
                    if self.job_active:
                        # print "\nG-code stream finished!"
                        # print "(LasaurGrbl may take some extra time to finalize)"
                        self.tx_buffer = ""
                        self.tx_index = 0
                        self.job_active = False
                        # ready whenever a job is done, including a status request via '?'
                        self.status['ready'] = True
            except OSError:
                # Serial port appears closed => reset
                self.close()
            except ValueError:
                # Serial port appears closed => reset
                self.close()
        else:
            # serial disconnected
            self.status['ready'] = False



    def process_status_line(self, line):
        if '#' in line[:3]:
            # print and ignore
            sys.stdout.write(line + "\n")
            sys.stdout.flush()
        elif '^' in line:
            sys.stdout.write("\nFEC Correction!\n")
            sys.stdout.flush()
        else:
            if '!' in line:
                # in stop mode
                self.cancel_queue()
                # not ready whenever in stop mode
                self.status['ready'] = False
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
            else:
                sys.stdout.write(".")
                sys.stdout.flush()

            if 'N' in line:
                self.status['bad_number_format_error'] = True
            if 'E' in line:
                self.status['expected_command_letter_error'] = True
            if 'U' in line:
                self.status['unsupported_statement_error'] = True

            if 'B' in line:  # Stop: Buffer Overflow
                self.status['buffer_overflow'] = True
            else:
                self.status['buffer_overflow'] = False

            if 'T' in line:  # Stop: Transmission Error
                self.status['transmission_error'] = True
            else:
                self.status['transmission_error'] = False

            if 'P' in line:  # Stop: Power is off
                self.status['power_off'] = True
            else:
                self.status['power_off'] = False

            if 'L' in line:  # Stop: A limit was hit
                self.status['limit_hit'] = True
            else:
                self.status['limit_hit'] = False

            if 'R' in line:  # Stop: by serial requested
                self.status['serial_stop_request'] = True
            else:
                self.status['serial_stop_request'] = False

            if 'D' in line:  # Warning: Door Open
                self.status['door_open'] = True
            else:
                self.status['door_open'] = False

            if 'C' in line:  # Warning: Chiller Off
                self.status['chiller_off'] = True
            else:
                self.status['chiller_off'] = False

            if 'X' in line:
                self.status['x'] = line[line.find('X')+1:line.find('Y')]
            # else:
            #     self.status['x'] = False

            if 'Y' in line:
                self.status['y'] = line[line.find('Y')+1:line.find('V')]
            # else:
            #     self.status['y'] = False

            if 'V' in line:
                self.status['firmware_version'] = line[line.find('V')+1:]





# singelton
SerialManager = SerialManagerClass()