import driveboard
import pulseraster
import json
import re

class DriveboardGcode:
    version = '# LasaurGrbl2 (pulseraster)'

    def __init__(self, serial_port, baudrate):
        self.driveboard = driveboard.Driveboard(serial_port, baudrate)

        # modal state of the gcode protocol (last used parameter)
        self.relative = False
        self.feedrate = None
        self.pulse_frequency = None
        self.pulse_duration = None
        self.x = None
        self.y = None
        self.z = None

    def connect(self):
        self.driveboard.connect()

    def disconnect(self, reason):
        self.driveboard.disconnect(reason)

    def is_connected(self):
        return self.driveboard.is_connected()

    def get_status(self):
        return self.driveboard.get_status()

    def status_request(self, arg):
        ## https://github.com/grbl/grbl/wiki/Interfacing-with-Grbl
        ## data = '<Idle,MPos:0.000,0.000,0.000,WPos:0.000,0.000,0.000>'
        #data = '<Idle,MPos:%.3f,%.3f,%.3f,WPos:0.000,0.000,0.000>' % \
        #        (st['INFO_POS_X'], st['INFO_POS_Y'], st['INFO_POS_Z'])

        status = self.driveboard.get_status()
        if arg == 'full':
            return 'status:' + json.dumps(status)
        elif arg == 'queue':
            return 'queue:%d,%.1f,%d' % (status['QUEUE_BACKEND'],
                                         status['QUEUE_FIRMBUF_PERCENT'],
                                         status['QUEUE_FIRMBUF'])
        elif not arg:
            if status['REPORT'] == 'ok':
                return 'status:ready or busy, but no error'
            else:
                return 'status:' + status['REPORT']
        else:
            return 'error:invalid status request'

    def set_intensity(self, value):
        pulse_frequency, pulse_duration = pulseraster.intensity2pulse(value)
        b = self.driveboard
        b.send_param('PARAM_PULSE_FREQUENCY', pulse_frequency)
        b.send_param('PARAM_PULSE_DURATION', pulse_duration)

    def gcode_line(self, line):
        print(line)
        line = line.split(';')[0].strip()  # remove gcode comments
        if not line:
            return
        if line == 'version':
            return self.version

        b = self.driveboard

        # those commands work even when disconnected:
        if line[0] == '?':
            # status request
            arg = line[1:].strip()
            return self.status_request(arg)
        elif line[0] == '~':
            # recover from stop condition
            b.connect()
            b.send_command('CMD_RESUME')
            return 'info:resume'

        if not b.is_connected():
            return 'error:disconnected - ' + b.get_disconnect_reason()

        if line[0] == '!':
            # instant stop
            b.send_command('CMD_STOP')
            return 'info:stop'
        # extract gcode parameters
        parts = re.split(r'([A-Z])', line)
        if parts[0] != '' or len(parts) < 3:
            return 'error:ignored unknown gcode %r' % line
        cmd = (parts[1] + parts[2]).strip()
        parts = parts[3:]

        args = {}
        while parts:
            letter = parts.pop(0).strip()
            try:
                value = float(parts.pop(0))
                args[letter] = value
            except ValueError:
                return 'error:gcode line ignored, could not parse float in %r' % line

        if cmd in ('G0', 'G1'):
            # move (G0: without lasing; G1: with lasing)
            if 'X' in args: b.send_param('PARAM_TARGET_X', args['X'])
            if 'Y' in args: b.send_param('PARAM_TARGET_Y', args['Y'])
            if 'Z' in args: b.send_param('PARAM_TARGET_Z', args['Z'])
            if 'F' in args: b.send_param('PARAM_FEEDRATE', args['F'])

            # consume arguments and keep track of state
            self.x = args.pop('X', self.x)
            self.y = args.pop('Y', self.y)
            self.z = args.pop('Z', self.z)
            self.feedrate = args.pop('F', self.feedrate)
            if self.relative:
                # not bothering to track position in relative mode
                self.x = None
                self.y = None
                self.z = None

            if cmd == 'G0':
                b.send_command('CMD_LINE_SEEK')
            elif cmd == 'G1':
                b.send_command('CMD_LINE_BURN')

        elif cmd == 'G90':
            b.send_command('CMD_REF_ABSOLUTE')
            self.relative = False
        elif cmd == 'G91':
            b.send_command('CMD_REF_RELATIVE')
            self.relative = True
        elif cmd == 'M80': b.send_command('CMD_AIR_ENABLE')
        elif cmd == 'M81': b.send_command('CMD_AIR_DISABLE')
        elif cmd == 'M82': b.send_command('CMD_AUX1_ENABLE')
        elif cmd == 'M83': b.send_command('CMD_AUX1_DISABLE')
        elif cmd == 'M84': b.send_command('CMD_AUX2_ENABLE')
        elif cmd == 'M85': b.send_command('CMD_AUX2_DISABLE')
        elif cmd == 'G10':
            # set offset
            # note: the firmware calls stepper_get_position_x/y/z and ignores the params
            #       (not sure if this is as intended)
            # note: LasaurGrbl docu talks about "L20" and "L2" - what is this? Not used by FW?
            p = args.pop('P')
            if p == 0: b.send_command('CMD_SET_OFFSET_TABLE')
            elif p == 1: b.send_command('CMD_SET_OFFSET_CUSTOM')
            else: return 'error:invalid set_offset command %r' % line
        elif cmd == 'G54':
            b.send_command('CMD_SEL_OFFSET_TABLE')
        elif cmd == 'G55':
            b.send_command('CMD_SEL_OFFSET_CUSTOM')
        elif cmd == 'G30':
            b.send_command('CMD_HOMING')
            # homing moves to the table offset (not always (0, 0))
            # make sure we send all target parameters for the next move
            self.x = None
            self.y = None
            self.z = None
        elif cmd[0] == 'S':
            # set intensity
            try:
                intensity = float(line[1:])
            except ValueError:
                self.set_intensity(0)
                return 'error:invalid S command %r, setting intensity to zero' % line
            if intensity < 0 or intensity > 255:
                self.set_intensity(0)
                return 'error:intensity out of range (0-255) %r, setting intensity to zero' % line
            value = intensity / 255.0
            self.set_intensity(value)
        else:
            return 'error:ignored unknown gcode command %r' % line
        if args:
            return 'error:ignored arguments %r of gcode line %r' % (args, line)
        return 'ok'
