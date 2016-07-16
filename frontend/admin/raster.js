'use strict';

angular.module('app.raster', ['app.core'])
.controller('RasterController', function ($scope, RasterLib) {
    var vm = this;

    const LASER_POWER = 100.0; // watts
    const RASTER_BYTES_MAX = 60;
    const PULSE_SECONDS = 31.875e-6;  // see laser.c
    const MINIMUM_PULSE_TICKS = 3;    // unit: PULSE_SECONDS
    const MAXIMUM_PULSE_TICKS = 127;  // unit: PULSE_SECONDS
    const ACCELERATION = 1800000.0    // mm/min^2, divide by (60*60) to get mm/sec^2

    vm.uploadedImage = null;

    vm.energy_density = 5.3;
    vm.img_w = 0;
    vm.img_h = 0;

    vm.requested_ppmm = 20.0;

    vm.haveImage = false;

    vm.actual_ppmm = null;
    vm.actual_pulse = null;

    vm.pulse_duration_us = function() {
        return vm.actual_pulse * PULSE_SECONDS / 1e-6;
    }

    vm.recalculate = function() {
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
            var pulse_density = vm.energy_density / energy_per_pulse;
            var ppmm = Math.sqrt(pulse_density);
            var error = Math.abs(vm.requested_ppmm - ppmm);
            if (pulse === MINIMUM_PULSE_TICKS || error < best_error) {
                best_pulse = pulse;
                best_ppmm = ppmm;
                best_error = error;
            }
        }

        vm.actual_ppmm = best_ppmm;
        vm.actual_pulse =  best_pulse;

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

    vm.recalculate();



    var preview_canvas = document.getElementById('preview-canvas');
    var preview_canvas_ctx = preview_canvas.getContext('2d');

    document.getElementById('file-input').addEventListener('change', onFileChanged, false);
    function onFileChanged(changeEvent) {
        var reader = new FileReader();
        reader.onload = function (loadEvent) {
            var img = new Image();
            img.onload = function(){
                $scope.$apply(function() {
                    vm.uploadedImage = img;
                    RasterLib.setImage(img);
                    RasterLib.process();
                    updatePreview();
                });
            }
            img.src = event.target.result;
        }
        reader.readAsDataURL(changeEvent.target.files[0]);
    }

    function updatePreview() {
        var src = RasterLib.grayCanvas;
        var w = src.width;
        var h = src.height;
        var cw = preview_canvas.width;
        var ch = preview_canvas.height;
        var ctx = preview_canvas_ctx;

        var scale = Math.min(cw/w, ch/h);

        ctx.clearRect(0, 0, cw, ch);
        ctx.save();
        ctx.scale(scale, scale);
        ctx.drawImage(src, 0, 0);
        ctx.restore();
    }


})
