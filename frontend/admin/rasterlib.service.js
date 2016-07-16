'use strict';

angular.module('app.rasterlib', ['app.core'])
.factory('RasterLib', function () {
    var sourceImg;
    var grayCanvas = document.createElement('canvas');
    var service = {
        setImage: setImage,
        process: process,
        grayCanvas: grayCanvas
        
    }
    return service;

    function setImage(img) {
        sourceImg = img;
    }

    function process() {
        var w = sourceImg.width;
        var h = sourceImg.height;

        // note: SVGs have some arbitrary width/height set by the browser, if we override it here the browser will vector-zoom
        grayCanvas.width = w;
        grayCanvas.height = h;
        var ctx = grayCanvas.getContext('2d');
        ctx.drawImage(sourceImg, 0, 0);

        var imageData = ctx.getImageData(0, 0, w, h);
        var pixels = imageData.data;

        // to grayscale
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

        // invert (black means high laser power)
        // TODO

        // scale image to output ppmm
        // TODO (preferably, allow interpolation to be set)

        // dithering (only if interpolation was enabled)
        // TODO

        // invert back for showing it as preview
        // TODO
    
        // convert to pulse image
        // TODO
        // img = PIL2array(img)
        // img[img>0] = pulse
    }
});
