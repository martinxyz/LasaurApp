'use strict';

angular.module('app.raster')
.factory('RasterLib', function () {
    var sourceImg;
    var grayCanvas = document.createElement('canvas');
    var pulseCanvas = document.createElement('canvas');
    var service = {
        setImage: setImage,
        grayCanvas: grayCanvas,
        pulseCanvas: pulseCanvas,
        makeGrayScale: makeGrayScale,
        makePulseImage: makePulseImage
    }
    return service;

    function setImage(img) {
        sourceImg = img;
        console.log('setImage');
    }

    function makeGrayScale() {
        var w = sourceImg.width;
        var h = sourceImg.height;
        console.log('makeGrayScale ' + w + ', ' + h);

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

    function makePulseImage(settings) {
        var input_w = grayCanvas.width;
        var input_h = grayCanvas.height;

        console.log('makePulseImage ' + input_w + ', ' + input_h);

        // scale image to output ppmm
        var w = settings.ppmm * settings.width;
        var scale = (settings.ppmm * settings.width) / input_w;
        var h = scale * input_h;
        w = Math.round(w);
        h = Math.round(h);

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

        // invert back for showing it as preview
        for (i = 0; i < w*h; i += 1) {
            var i4 = i*4;
            pixels[i4+0] = 255 - arr[i];
            pixels[i4+1] = 255 - arr[i];
            pixels[i4+2] = 255 - arr[i];
            pixels[i4+3] = 255;
        }

        ctx.putImageData(imageData, 0, 0);
    
        // convert to pulse image
        // img = PIL2array(img)
        // img[img>0] = pulse

        /*
          accel_dist = 0.5 * feedrate**2 / b.ACCELERATION
          lead_in_max = accel_dist * 1.2
          lead_in = min(settings.lead_in, lead_in_max)
          print 'lead-in: %.2f mm' % lead_in

          b.feedrate(feedrate)
          raster_execute(b, img, x0, y0, settings.ppmm, settings.ppmm, settings.skip_empty, settings.bidirectional, lead_in)
        */
        console.log('makePulseImage put result ' + w + ', ' + h);
    }
    
});
