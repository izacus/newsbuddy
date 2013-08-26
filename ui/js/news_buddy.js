angular.module("NewsBuddy", ['ngRoute', 'ngSanitize', 'infinite-scroll']).
       config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {
            $locationProvider.hashPrefix('!').html5Mode(false);
            $routeProvider
                .when('/latest', { templateUrl: 'partials/search_results.html', controller: "SearchController" })
                .when('/stats', { templateUrl: 'partials/stats.html', controller: "StatsController" })
                .otherwise({ redirectTo: "/latest" });
      }]);