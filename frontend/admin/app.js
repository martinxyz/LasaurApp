'use strict';

angular.module('app', [
    'app.core',
    'app.raster',
    'app.admin'
])

    // routing

.config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise('/admin');
    
    $stateProvider

        .state('admin', {
            url: '/admin',
            templateUrl: 'admin.html'
        })
        .state('raster', {
            url: '/raster',
            templateUrl: 'raster.html'
        })
});
