var newsBuddy = angular.module('NewsBuddy', []);

newsBuddy.controller('StatsController', function($scope, $http) {
    $scope.stats = { "total_news" : 0, "news_today": 0 };

    $http.get('/news/stats/').success(function data(data) {
        $scope.stats = data;
    });
});