'use strict';

var app = angular.module("LasaurAdmin", [])
app.controller('AdminController', function ($scope, $http) {

    $scope.firmware_version = 'not asked yet';
    $scope.config = {};


    $http.get('/config').then(function(response) {
        var config = response.data;
        $scope.work_area_width = config.workspace[0];
        $scope.work_area_height = config.workspace[1];
        $scope.config = config;
    });
})
