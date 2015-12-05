#!/usr/bin/env python
import sys, os, time, random, math
import numpy as np
from PIL import Image, ImageOps
import argparse
from config import conf
import driveboard

def raster_execute(b, pulse_duration_image, x0, y0, ppmm_x, ppmm_y, skip_empty=True, bidirectional=False, lead_in=5.0):
    """Execute the rastering of a pulse-duration image."""
    assert pulse_duration_image.dtype == 'uint8'
    assert pulse_duration_image.max() < 128, 'image contains pulse durations that are not feasible'

    b.intensity(0)
    direction = +1
    for lineno, data in enumerate(pulse_duration_image):
        y = y0 + lineno/ppmm_y
        x = x0

        if skip_empty:
            if not data.any():
                continue
            nz, = data.nonzero()
            first, last = nz[0], nz[-1]
            x += first/ppmm_x
            data = data[first:last+1]

        if direction == -1:
            # A raster move always starts with a pulse, and ends with no pulse.
            #     0---1---2---3---|  forward
            # |---0---1---2---3      backward
            data = data[::-1] # reverse
            x += (len(data)-1)/ppmm_x

        if lead_in:
            b.move(x-direction*lead_in, y)
        b.move(x, y)
        x += direction*len(data)/ppmm_x
        b.raster_move(x, y, data)
        if lead_in:
            b.move(x+direction*lead_in, y)

        if bidirectional:
            direction *= -1
    

def prepare_and_engrave(b, img, x0, y0, settings):
    """Scale and convert and engrave an image."""

    # Current method: (optimized towards bi-level images)
    # - choose a pulse_duration
    # - adjust ppmm such that black pixels have the correct energy_density
    # - scale image according to ppmm
    # - use dithering for mid-tones (shorter pulses are not used)
    # - decrease feedrate if required to implement high energy_density or high ppmm

    s = settings
    laser_power = 100.0 # watts
    
    # calculate ppmm for each allowed pulse duration
    pulse = np.arange(b.MINIMUM_PULSE_TICKS, b.MAXIMUM_PULSE_TICKS+1)
    pulse_duration = pulse * b.PULSE_SECONDS
    energy_per_pulse = pulse_duration * laser_power # joules
    pulse_density = s.energy_density / energy_per_pulse
    ppmm = np.sqrt(pulse_density)
    
    # choose the ppmm closest to the target
    error = np.abs(ppmm - s.ppmm)
    i = np.argmin(error)
    pulse = pulse[i]
    ppmm  = ppmm[i]
    print 'desired ppmm %.3f, actual ppmm %.3f, pulse %d (%.0f us)' % (s.ppmm, ppmm, pulse, pulse * b.PULSE_SECONDS / 1e-6)
    
    feedrate = s.max_feedrate

    # limit feedrate such that max_intensity is respected
    feedrate_max = s.max_intensity/100.0 / (ppmm * (pulse * b.PULSE_SECONDS)) * 60 
    print 'feedrate_max (because of max_intensity)', feedrate_max
    feedrate = min(feedrate, feedrate_max)

    # limit feedrate such that the driveboard will not slow down to wait for serial data
    byte_per_second = conf['baudrate']/10/2 # (8 bits + startbit + stopbit) and every byte is sent twice (error detection)
    byte_per_second *= 0.5 # leave some room for parameters and line commands
    feedrate_max = byte_per_second / ppmm * 60.0
    print 'feedrate_max (because of baudrate limit)', feedrate_max
    feedrate = min(feedrate, feedrate_max)

    print 'feedrate', feedrate
    print 'black intensity/duty: %.1f%%' % (ppmm * (pulse * b.PULSE_SECONDS) * (feedrate / 60) * 100)


    # scale image to output ppmm
    img = img.convert('L') # grayscale
    img = ImageOps.invert(img) # black means high power
    input_w, input_h = img.size
    w = ppmm * s.width
    h = w / float(input_w) * input_h
    w, h = int(round(w)), int(round(h))
    if s.binary:
        img = img.resize((w, h), Image.NEAREST)
        #img.save('debug1.png')
        img = img.convert('1', dither=Image.NONE)
    else:
        img = img.resize((w, h), Image.ANTIALIAS)
        #img.save('debug1.png')
        img = img.convert('1', dither=Image.FLOYDSTEINBERG)
    #img.save('debug2.png')
    
    img = np.array(img, dtype='uint8')
    img[img>0] = pulse
    #print img, img.mean(), img.max()

    accel_dist = 0.5 * feedrate**2 / b.ACCELERATION
    lead_in_max = accel_dist * 1.2
    lead_in = min(s.lead_in, lead_in_max)
    print 'lead-in: %.2f mm' % lead_in

    b.feedrate(feedrate)
    raster_execute(b, img, x0, y0, ppmm, ppmm, s.skip_empty, s.bidirectional, lead_in)
    
    return w/ppmm, h/ppmm


def cut_box(b, x, y, w, h, cut_feedrate, cut_intensity):
    b.intensity(0)
    b.move(x, y)
    b.feedrate(cut_feedrate)
    b.intensity(cut_intensity)
    b.move(x+w, y)
    b.move(x+w, y+h)
    b.move(x, y+h)
    b.move(x, y)
    b.intensity(0)

def job(b, args):
    if args.cut:
        box_spacing = 5.0
    else:
        box_spacing = 0.0

    x0 = max(box_spacing, args.lead_in)
    y0 = box_spacing

    w, h = prepare_and_engrave(b, Image.open(args.filename[0]), x0, y0, settings=args)
    if args.cut:
        cut_box(b, x0 - box_spacing, y0 - box_spacing, w + 2*box_spacing, h + 2*box_spacing,
                args.cut_feedrate, args.cut_intensity)
    b.move(0, 0)

def wait():
    print 'waiting for job to execute...'
    # wait for job to finish
    time.sleep(2.0) # wait for next status update
    while True:
        s = driveboard.status()
        print s
        if s['stops']:
            print s
            raise RuntimeError
        if s['ready']:
            break
        time.sleep(2)
    print 'done.'

if __name__ == '__main__':

    p = argparse.ArgumentParser(description="Raster-engrave an image.")
    p.add_argument('filename', nargs=1, metavar='FILENAME',
                   help='PNG, JPEG or SVG file to be raster-engraved')

    p.add_argument('-w', '--width', type=float, required=True,
                   help='width (mm) of the image (height is calculated)')

    p.add_argument('-e', '--energy-density', required=True, type=float,
                   help='exposure of fully black areas (Ws per mm^2), about 0.4 to clearly mark wood, 0.9 to engrave wood')

    p.add_argument('-f', '--max-feedrate', default=8000, type=float,
                   help='maximum feedrate (mm/min)')

    p.add_argument('--max-intensity', type=float, default=80,
                   help='maximum laser intensity or duty (in percent), enforced by reducing the feedrate (default: 80)')

    p.add_argument('--binary', action='store_true',
                   help='binary mode (disables dithering and interpolation)')

    p.add_argument('--ppmm', default=20.0, type=float,
                   help='desired pulses per mm (of the laser output), default 20.0, will usually be lower because of the minimum pulse duration, unless the requested energy density is high enough')

    p.add_argument('--bidirectional', action='store_true',
                   help='raster in both directions (twice as fast, probably worse quality)')

    p.add_argument('--skip-empty', action='store_true',
                   help='skip white pixels (faster, but maybe it can affect quality)')

    p.add_argument('--lead-in', default=20.0, type=float,
                   help='distance (mm) for acceleration before and after raster lines (default: 20mm; it can be very low or zero; will be limited to 120%% of the calculated acceleration distance)')

    p.add_argument('-c', '--cut', action='store_true',
                   help='cut a box around the result')
    p.add_argument('--cut-feedrate', default=1300, type=float,
                   help='feedrate for cutting the box, default: 1300')
    p.add_argument('--cut-intensity', default=60, type=float,
                   help='intensity (in percent) for cutting the box, default: 60')

    p.add_argument('-s', '--simulation', action='store_true',
                   help='do not connect to laser, use simulation and print statistics')
    args = p.parse_args()
    print args

    #"inkscape --without-gui --file=filename.svg --export-area-drawing --export-background=white --export-dpi=88.9 --export-png 'foo.png'"

    print vars(args)


    if args.simulation:
        print 'simulation...'
        import simulation
        sim = simulation.Simulator()
        job(sim, args)
        sim.report()
        print 'simulation done.'
        sys.exit(0)

    try:
        driveboard.connect()
        assert driveboard.connected()
        print driveboard.status()
        job(driveboard, args)
        wait()
    finally:
        driveboard.close()
