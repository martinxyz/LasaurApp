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
        # self.pulse_frequency = None
        # self.pulse_duration = None
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
            return json.dumps(status['queue'])
        elif not arg:
            if status['error_report']:
                return 'status:' + status['error_report']
            elif status['ready']:
                return 'status:ready'
            else:
                return 'status:busy'
        else:
            return 'error:invalid status request'

    def special_line(self, line):
        # those commands work even when disconnected:
        if line[0] == '?':
            # status request
            arg = line[1:].strip()
            return self.status_request(arg)
        elif line == '!' or line == '!stop':
            # instant stop
            self.driveboard.send_command('CMD_STOP')
            return 'info:stopping'
        elif line == '~' or line == '!resume':
            # recover from all stop conditions
            error = self.driveboard.connect()
            if error: return 'error:' + error
            self.driveboard.send_command('CMD_RESUME')
            self.driveboard.unpause()
            return 'info:resuming'
        elif line == '!pause':
            self.driveboard.pause()
            return 'info:pausing'
        elif line == '!unpause':
            self.driveboard.unpause()
            return 'info:continuing'
        elif line == '!version':
            return 'info:' + self.version
        else:
            return 'error:invalid command'

    def gcode_line(self, line):
        line = line.split(';')[0].strip()  # remove gcode comments
        if not line:
            return ''

        if line[0] in '?!~':
            return self.special_line(line)

        if not self.driveboard.is_connected():
            return 'error:' + self.driveboard.get_disconnect_reason()

        # extract gcode parameters
        parts = re.split(r'([A-Z])', line)
        if parts[0] != '' or len(parts) < 3:
            return 'error:ignored unknown gcode %r' % line
        try:
            # this way, we support both G00 and G0
            cmd = (parts[1] + str(int(parts[2]))).strip()
        except ValueError:
            return 'error:gcode line ignored, could not parse int in %r' % line
        parts = parts[3:]

        args = {}
        while parts:
            letter = parts.pop(0).strip()
            try:
                value = float(parts.pop(0))
                args[letter] = value
            except ValueError:
                return 'error:gcode line ignored, could not parse float in %r' % line

        # result of parsing
        params = []
        command = None
        intensity_value = None

        if cmd in ('G0', 'G1'):
            # move (G0: without lasing; G1: with lasing)
            if 'X' in args: params.append(('PARAM_TARGET_X', args['X']))
            if 'Y' in args: params.append(('PARAM_TARGET_Y', args['Y']))
            if 'Z' in args: params.append(('PARAM_TARGET_Z', args['Z']))
            if 'F' in args: params.append(('PARAM_FEEDRATE', args['F']))

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
                command = 'CMD_LINE_SEEK'
            elif cmd == 'G1':
                command = 'CMD_LINE_BURN'
                intensity_value = args.pop('S', None)

        elif cmd == 'G90':
            command = 'CMD_REF_ABSOLUTE'
            self.relative = False
        elif cmd == 'G91':
            command = 'CMD_REF_RELATIVE'
            self.relative = True
        elif cmd == 'M80': command = 'CMD_AIR_ENABLE'
        elif cmd == 'M81': command = 'CMD_AIR_DISABLE'
        elif cmd == 'M82': command = 'CMD_AUX1_ENABLE'
        elif cmd == 'M83': command = 'CMD_AUX1_DISABLE'
        elif cmd == 'M84': command = 'CMD_AUX2_ENABLE'
        elif cmd == 'M85': command = 'CMD_AUX2_DISABLE'
        elif cmd == 'G10':
            # set offset
            # note: the firmware calls stepper_get_position_x/y/z and ignores the params
            #       (not sure if this is as intended)
            # note: LasaurGrbl docu talks about "L20" and "L2" - what is this? Not used by FW?
            p = args.pop('P')
            if p == 0: command = 'CMD_SET_OFFSET_TABLE'
            elif p == 1: command = 'CMD_SET_OFFSET_CUSTOM'
            else: return 'error:invalid set_offset command %r' % line
        elif cmd == 'G54':
            command = 'CMD_SEL_OFFSET_TABLE'
        elif cmd == 'G55':
            command = 'CMD_SEL_OFFSET_CUSTOM'
        elif cmd == 'G30':
            command = 'CMD_HOMING'
            # homing moves to the table offset (not always (0, 0))
            self.x = None
            self.y = None
            self.z = None
        elif cmd[0] == 'S':
            # set intensity
            intensity_value = line[1:]
        else:
            return 'error:unknown gcode command %r' % line
        if args:
            return 'error:unknown arguments %r in gcode line %r' % (args, line)

        if intensity_value is not None:
            try:
                intensity = float(intensity_value)
            except ValueError:
                return 'error:invalid intensity %r' % line
            if intensity < 0 or intensity > 255:
                return 'error:intensity out of range (0-255) %r' % line
            frequency, duration = pulseraster.intensity2pulse(intensity)
            params.append(('PARAM_PULSE_FREQUENCY', frequency))
            params.append(('PARAM_PULSE_DURATION', duration))

        # execute
        for name, value in params:
            self.driveboard.send_param(name, value)
        if command:
            self.driveboard.send_command(command)
        return 'ok'
