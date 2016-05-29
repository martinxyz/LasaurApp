'use strict';

var app = angular.module("RasterApp", [])
app.controller('RasterController', function ($scope) {
    const LASER_POWER = 100.0; // watts
    const RASTER_BYTES_MAX = 60;
    const PULSE_SECONDS = 31.875e-6;  // see laser.c
    const MINIMUM_PULSE_TICKS = 3;    // unit: PULSE_SECONDS
    const MAXIMUM_PULSE_TICKS = 127;  // unit: PULSE_SECONDS
    const ACCELERATION = 1800000.0    // mm/min^2, divide by (60*60) to get mm/sec^2

    $scope.energy_density = 5.3;
    $scope.img_w = 200;
    $scope.img_h = 250;

    $scope.requested_ppmm = 20.0;

    $scope.actual_ppmm = null;
    $scope.actual_pulse = null;

    $scope.pulse_duration_us = function() {
        return $scope.actual_pulse * PULSE_SECONDS / 1e-6;
    }

    $scope.recalculate = function() {
        // Current method: (optimized towards bi-level images)
        // - choose a pulse_duration
        // - adjust ppmm such that black pixels have the correct energy_density
        // - scale image according to ppmm
        // - use dithering for mid-tones (shorter pulses are not used)
        // - decrease feedrate if required to implement high energy_density or high ppmm

        // Calculate ppmm for each allowed pulse duration,
        // and choose the ppmm closest to the target.
        var best_pulse;
        var best_ppmm;
        var best_error;
        for (var pulse = MINIMUM_PULSE_TICKS; pulse <= MAXIMUM_PULSE_TICKS; pulse++) {
            var pulse_duration = pulse * PULSE_SECONDS;
            var energy_per_pulse = pulse_duration * LASER_POWER;  // joules
            var pulse_density = $scope.energy_density / energy_per_pulse;
            var ppmm = Math.sqrt(pulse_density);
            var error = Math.abs($scope.requested_ppmm - ppmm);
            if (pulse === MINIMUM_PULSE_TICKS || error < best_error) {
                best_pulse = pulse;
                best_ppmm = ppmm;
                best_error = error;
            }
        }

        $scope.actual_ppmm = best_ppmm;
        $scope.actual_pulse =  best_pulse;

        /*
        error = np.abs(ppmm - s.ppmm)
        i = np.argmin(error)
        pulse = pulse[i]
        ppmm = ppmm[i]
        print 'desired ppmm %.3f, actual ppmm %.3f, pulse %d (%.0f us)' % (s.ppmm, ppmm, pulse, pulse * b.PULSE_SECONDS / 1e-6)

        feedrate = s.max_feedrate

        // limit feedrate such that max_intensity is respected
        feedrate_max = s.max_intensity/100.0 / (ppmm * (pulse * b.PULSE_SECONDS)) * 60
        print 'feedrate limit because of max_intensity: %.0f mm/min' % feedrate_max
        feedrate = min(feedrate, feedrate_max)

        // limit feedrate such that the driveboard will not slow down to wait for serial data
        byte_per_second = conf['baudrate']/10/2 # (8 bits + startbit + stopbit) and every byte is sent twice (error detection)
        byte_per_second *= 0.5 # leave some room for parameters and line commands
        feedrate_max = byte_per_second / ppmm * 60.0
        print 'feedrate limit because of baudrate limit: %.0f mm/min' % feedrate_max
        feedrate = min(feedrate, feedrate_max)

        print 'feedrate %.0f' % feedrate
        print 'intensity (or duty) for full black: %.1f%%' % (ppmm * (pulse * b.PULSE_SECONDS) * (feedrate / 60) * 100)
        */
    }

    $scope.recalculate();

})

