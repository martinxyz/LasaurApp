'use strict';

angular.module('app.raster')
.factory('RasterLib', function () {
    var sourceImg;
    var grayCanvas = document.createElement('canvas');
    var pulseCanvas = document.createElement('canvas');
    var pulseArray = null;
    var service = {
        setImage: setImage,
        grayCanvas: grayCanvas,
        pulseCanvas: pulseCanvas,
        makeGrayScale: makeGrayScale,
        makePulseImage: makePulseImage,
        makeGcode: makeGcode
    }
    return service;

    function setImage(img) {
        sourceImg = img;
    }

    function makeGrayScale() {
        var w = sourceImg.width;
        var h = sourceImg.height;

        // note: for SVGs we have some arbitrary width/height set by
        // the browser, if we did override it here the browser would
        // vector-zoom
        grayCanvas.width = w;
        grayCanvas.height = h;
        var ctx = grayCanvas.getContext('2d');
        ctx.drawImage(sourceImg, 0, 0);

        var imageData = ctx.getImageData(0, 0, w, h);
        var pixels = imageData.data;

        for (var i = 0; i < pixels.length; i += 4) {
            var alpha = pixels[i+3]/255.0;
            var gray = (pixels[i]*0.299 + pixels[i+1]*0.587 + pixels[i+2]*0.114) / 255.0;
            // remove transparency (use white background)
            gray = alpha * gray + (1.0-alpha);
            gray = gray * 255.0;

            pixels[i+0] = gray;
            pixels[i+1] = gray;
            pixels[i+2] = gray;
            pixels[i+3] = 255;
        }

        ctx.putImageData(imageData, 0, 0);
    }

    function makePulseImage(params) {
        var input_w = grayCanvas.width;
        var input_h = grayCanvas.height;

        // scale image to output ppmm
        var w = params.ppmm * params.width;
        var scale = (params.ppmm * params.width) / input_w;
        var h = scale * input_h;
        w = Math.round(w);
        h = Math.round(h);

        if (w == 0 || h == 0) {
            pulseCanvas.width = 0;
            pulseCanvas.height = 0;
            return;
        }

        pulseCanvas.width = w;
        pulseCanvas.height = h;
        var ctx = pulseCanvas.getContext('2d');

        ctx.clearRect(0, 0, w, h);
        ctx.save();
        ctx.scale(scale, scale);
        ctx.drawImage(grayCanvas, 0, 0);
        // TODO: choose interpolation method
        // TODO: interpolate in linear light, not in sRGB (don't let the browser do it)
        ctx.restore();

        // TODO: convert sRGB to linear light
        // TODO: allow custom gamma correction (laser/material)

        // invert (black means high power)
        var imageData = ctx.getImageData(0, 0, w, h);
        var pixels = imageData.data;
        var arr = new Uint8ClampedArray(w*h);
        for (var i = 0; i < w*h; i += 1) {
            arr[i] = 255 - pixels[i*4];
        }

        // dithering
        // source: http://blog.ivank.net/floyd-steinberg-dithering-in-javascript.html
        // with bugfix concerning error rounding
        function floydSteinberg(sb, w, h)   // source buffer, width, height
        {
            for(var i=0; i<h; i++)
                for(var j=0; j<w; j++)
            {
                var ci = i*w+j;               // current buffer index
                var cc = sb[ci];              // current color
                var rc = (cc<128?0:255);      // real (rounded) color
                var err = cc-rc;              // error amount
                sb[ci] = rc;                  // saving real color
                if(j+1<w) sb[ci  +1] += (err*7)>>4;  // if right neighbour exists
                if(i+1==h) continue;   // if we are in the last line
                if(j  >0) sb[ci+w-1] += (err*3)>>4;  // bottom left neighbour
                sb[ci+w  ] += (err*5)>>4;  // bottom neighbour
                if(j+1<w) sb[ci+w+1] += err - (err*7)>>4 - (err*3)>>4;  // bottom right neighbour
            }
        }
        floydSteinberg(arr, w, h);

        // export to pulseArray (for execution) and to canvas (for preview)
        for (i = 0; i < w*h; i += 1) {
            // preview
            var i4 = i*4;
            pixels[i4+0] = 255 - arr[i];
            pixels[i4+1] = 255 - arr[i];
            pixels[i4+2] = 255 - arr[i];
            pixels[i4+3] = 255;

            // pulse duration bytes
            if (arr[i] !== 0) arr[i] = params.pulse;
        }
        ctx.putImageData(imageData, 0, 0);
        pulseArray = arr;
        pulseArray.w = w;
        pulseArray.h = h;

        return h;
    }

    function makeGcode(params)  {
        var arr = pulseArray;
        var w = pulseArray.w;
        var h = pulseArray.h;

        var x0 = params.pos_x;
        var y0 = params.pos_y;
        var lead_in = params.lead_in;
        var ppmm_x = params.ppmm;
        var ppmm_y = params.ppmm;
        var bidirectional = params.bidirectional;
        var skip_empty = params.skip_empty;

        // Execute the rastering of a pulse-duration image
        // assert pulse_duration_image.max() < 128, 'image contains pulse durations that are not feasible'

        var gcode_result = '';
        function gcode(line) {
            gcode_result += line + '\n';
        }
        var gcode_x;
        var gcode_y;
        function move(x, y) {
            gcode('G0 X' + x.toFixed(3) + ' Y' + y.toFixed(3));
            gcode_x = x;
            gcode_y = y;
        }
        function raster_move(target_x, target_y, data) {
            // split large move into smaller chunks
            const RASTER_BYTES_MAX = 60;  // firmware buffer size
            var bytes_total = data.length;
            while (data.length > 0) {
                var chunk = data.slice(0, RASTER_BYTES_MAX);
                data = data.slice(RASTER_BYTES_MAX);
                var fac = data.length / bytes_total;
                var px = fac*gcode_x + (1-fac)*target_x;
                var py = fac*gcode_y + (1-fac)*target_y;

                // G7 (raster-line) command
                var b64encoded = btoa(String.fromCharCode.apply(null, chunk));
                gcode('G7 X' + px.toFixed(3) + ' Y' + py.toFixed(3) + 'V1 D' + b64encoded);
            }
            gcode_x = target_x;
            gcode_y = target_y;
        }

        // set intensity to zero; the raster-move implicitly defines its own intensity
        gcode('S0');
        gcode('G0 F' + params.feedrate.toFixed(3));

        var direction = +1;
        for (var lineno=0; lineno < h; lineno++) {
            var y = y0 + lineno/ppmm_y;
            var x = x0;

            var data = arr.slice(w*lineno, w*(lineno+1));

            if (skip_empty) {
                var first = -1;
                var last = -1;
                for (var i=0; i<data.length; i++) {
                    if (data[i] !== 0) {
                        if (first === -1) first = i;
                        last = i;
                    }
                }
                if (first === -1) continue;
                x += first/ppmm_x
                data = data.slice(first, last+1);
            }

            if (direction === -1) {
                // A raster move always starts with a pulse, and ends with no pulse.
                //     0---1---2---3---|  forward
                // |---0---1---2---3      backward
                data.reverse();
                x += (data.length-1)/ppmm_x;
            }

            if (lead_in) {
                move(x-direction*lead_in, y);
            }
            move(x, y);
            x += direction*data.length/ppmm_x;
            raster_move(x, y, data)
            if (lead_in) {
                move(x+direction*lead_in, y);
            }

            if (bidirectional) {
                direction *= -1;
            }
        }
        return gcode_result;
    }
});
