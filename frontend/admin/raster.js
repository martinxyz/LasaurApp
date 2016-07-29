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
    const BAUDRATE = 57600;

    vm.uploadedImage = null;

    vm.img_w = 0;
    vm.img_h = 0;

    vm.haveImage = false;

    vm.requested_ppmm = 18.0;
    vm.requested_pulse = null;
    vm.max_feedrate = 8000;
    vm.max_intensity = 80;

    vm.params = {
        // set directly
        width: 20.0,
        energy_density: 0.7,
        binary: false,
        bidirectional: false,
        skip_empty: true,
        lead_in: 2.0,
        pos_x: 0.0,
        pos_y: 0.0,
        // calculated
        ppmm: null,
        feedrate: null
    }

    vm.pulse_duration_us = function() {
        return vm.params.pulse * PULSE_SECONDS / 1e-6;
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
        var params = vm.params;
        for (var pulse = MINIMUM_PULSE_TICKS; pulse <= MAXIMUM_PULSE_TICKS; pulse++) {
            var pulse_duration = pulse * PULSE_SECONDS;
            var energy_per_pulse = pulse_duration * LASER_POWER;  // joules
            var pulse_density = params.energy_density / energy_per_pulse;
            var ppmm = Math.sqrt(pulse_density);
            var error = Math.abs(vm.requested_ppmm - ppmm);
            if (pulse === MINIMUM_PULSE_TICKS || error < best_error) {
                best_pulse = pulse;
                best_ppmm = ppmm;
                best_error = error;
            }
        }

        vm.params.pulse = best_pulse;
        vm.params.ppmm = best_ppmm;

        var feedrate = vm.max_feedrate;

        // limit feedrate such that max_intensity is respected
        var feedrate_limit1 = params.max_intensity/100.0 / (ppmm * (pulse * PULSE_SECONDS)) * 60;
        feedrate = Math.min(feedrate, feedrate_limit1);

        // limit feedrate such that the driveboard will not slow down to wait for serial data
        var byte_per_second = BAUDRATE/10/2;  // (8 bits + startbit + stopbit) and every byte is sent twice (error detection)
        byte_per_second *= 0.5  // leave some room for parameters and line commands (just a rough guess)
        var feedrate_limit2 = byte_per_second / ppmm * 60.0
        feedrate = Math.min(feedrate, feedrate_limit2);

        vm.params.feedrate = feedrate;

        // vm.actual_intensity = ppmm * (pulse * PULSE_SECONDS) * (feedrate / 60) * 100;

        RasterLib.makeGrayScale();
        RasterLib.makePulseImage(vm.params);
        updatePulsePreview();
        updateGrayScalePreview();
    }

    vm.canvas_gray = null;
    vm.canvas_pulse = null;

    document.getElementById('file-input').addEventListener('change', onFileChanged, false);
    function onFileChanged(changeEvent) {
        var reader = new FileReader();
        reader.onload = fileLoaded;
        reader.readAsDataURL(changeEvent.target.files[0]);
        function fileLoaded(loadEvent) {
            var img = new Image();
            img.onload = imageLoaded;
            img.src = event.target.result;
            function imageLoaded() {
                $scope.$apply(function() {
                    setImage(img);
                });
            }
        }
    }

    // for development/debugging
    function debugInit() {
        var img = new Image();
        img.onload = imageLoaded;
        img.src = 'img.jpg';
        function imageLoaded() {
            $scope.$apply(function() {
                setImage(img);
            });
        }
    }
    debugInit();

    function setImage(img) {
        vm.uploadedImage = img;
        RasterLib.setImage(img);
        vm.recalculate();
    }

    function updateGrayScalePreview() {
        console.log('updateGrayScalePreview');
        vm.canvas_gray = RasterLib.grayCanvas;
        if (vm.canvas_gray.modified) {
            vm.canvas_gray.modified += 1;
        } else {
            vm.canvas_gray.modified = 1;
        }
    }

    function updatePulsePreview() {
        console.log('updatePulsePreview');
        vm.canvas_pulse = RasterLib.pulseCanvas;
        if (vm.canvas_pulse.modified) {
            vm.canvas_pulse.modified += 1;
        } else {
            vm.canvas_pulse.modified = 1;
        }
    }
})
