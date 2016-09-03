angular.module('app.raster')
.directive('rasterPreview', function () {
    var directive = {
        restrict: 'E',
        scope: {
            img: '=',
            width: '=',
            height: '='
        },
        template: '<canvas />',
        link: link
    };
    return directive;

    function link(scope, element, attrs) {
        // element.on('mousemove', mousemove);
        var canvas = element[0].firstChild;
        var ctx = canvas.getContext('2d');
        var el = $(canvas);

        canvas.width = scope.width;
        canvas.height = scope.height;

        var percent_x = 0.5;
        var percent_y = 0.5;
        var zoomed = false;
        scope.$watch("img", reset);
        scope.$watch("img.modified", reset);
        el.mouseleave(reset);

        el.mousemove(function(event) {
            var offset = el.offset();
            percent_x = (event.pageX - offset.left) / el.width();
            percent_y = (event.pageY - offset.top) / el.height();

            // add some empty border
            percent_x = percent_x * 1.2 - 0.1;
            percent_y = percent_y * 1.2 - 0.1;

            zoomed = true;

            redraw();
        });

        function reset() {
            percent_x = 0.5;
            percent_y = 0.5;
            zoomed = false;
            redraw();
        }

        function redraw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            var img = scope.img;
            if (img === null) return;

            if (zoomed) {
                var zoom = 3.0;
            } else {
                // zoom to fit
                zoom = Math.min(
                    canvas.width / img.width ,
                    canvas.height / img.height);
            }
            var oversize_w = zoom*img.width - canvas.width;
            var oversize_h = zoom*img.height - canvas.height;

            var px = -percent_x*oversize_w;
            var py = -percent_y*oversize_h;

            if (oversize_w < 0) px = -oversize_w/2;
            if (oversize_h < 0) py = -oversize_h/2;

            px = Math.round(px);
            py = Math.round(py);

            ctx.mozImageSmoothingEnabled = false;
            ctx.webkitImageSmoothingEnabled = false;
            ctx.msImageSmoothingEnabled = false;
            ctx.imageSmoothingEnabled = false;

            ctx.drawImage(img, px, py,
                          zoom*img.width, zoom*img.height);
        }
    }
});
