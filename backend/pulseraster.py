import math
from driveboard import PULSE_SECONDS

def intensity2pulse(intensity, emulate_old_method=False):
    """Convert laser intensity (in percent) to pulse parameters"""
    value = intensity / 255.0
    assert value <= 1.0 and value >= 0.0
    if emulate_old_method:
        # approximate what the old firmware did
        old_intensity = value * 255.0
        if old_intensity > 40:
            freq_hz = 3900
        elif old_intensity > 10:
            freq_hz = 489
        else:
            freq_hz = 122
        # find closest feasible pulse duration (rounding up to avoid higher frequencies)
        pulse = math.ceil(value * 1.0/freq_hz / PULSE_SECONDS)
        if pulse > 0:
            # find a slightly better frequency
            freq_hz = 1.0 / (pulse * PULSE_SECONDS / value)
    else:
        if value == 0:
            pulse = 0
            freq_hz = 0
        else:
            pulse = 3 + math.floor(6 * value)
            freq_hz = 1.0 / (pulse * PULSE_SECONDS / value)

    if value > .99:
        pulse += 1 # make sure pulses overlap slightly

    #print '--> %d Hz, pulse duration %dus' % (freq_hz, pulse * PULSE_SECONDS / 1e-6)
    return freq_hz, pulse
