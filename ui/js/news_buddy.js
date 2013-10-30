window.news_buddy = angular.module("NewsBuddy", ['ngRoute', 'ngSanitize', 'infinite-scroll', 'typeahead.directives']).
       config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {
            $locationProvider.hashPrefix('!').html5Mode(false);
            $routeProvider
                .when('/latest', { templateUrl: 'partials/search_results.html', controller: "SearchController" })
                .when('/stats', { templateUrl: 'partials/stats.html', controller: "StatsController" })
                .when('/detail/:resultId', { templateUrl: 'partials/details.html', controller: "DetailsController" })
                .otherwise({ redirectTo: "/latest" });
      }]);
