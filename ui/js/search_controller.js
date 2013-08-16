var newsBuddy = angular.module('NewsBuddy', ['infinite-scroll']);

newsBuddy.controller('SearchController', function($scope, $http) {

    $scope.offset = 0;
    $scope.all_loaded = false;
    $scope.results_array = [];

    $scope.search = function() {
        $scope.offset = 0;
        $scope.results = {};
        $scope.results_array = [];      // Array to show results
        $scope.sources = null;
        $scope.publish_dates = null;
        $scope.all_loaded = false;
        $scope.loadPage();
    };

    $scope.loadPage = function()
    {
        console.info($scope)
        if ($scope.loading)
            return;

        if (!$scope.query)
            return;

        $scope.loading = true;
        $http.get('/news/query/?offset=' + $scope.offset + '&q=' + $scope.query).success(function data(data) {
            $scope.applyResults(data["results"]);
            //$scope.results.push.apply($scope.results, data["results"]);

            if (data["facets"]["source"] != null) {
                $scope.sources = data["facets"]["source"];
                // Sort sources by number of hits descending
                $scope.sources.sort(function (a, b) {
                    return b[1] - a[1];
                });
            }
            
            if (data["facets"]["published"] != null) {
                $scope.publish_dates = data["facets"]["published"]
                // Sort publish dates by date descending as well
                $scope.publish_dates.sort(function (a,b) {
                    if (a[0] > b[0])
                        return -1;
                    else if (a[0] < b[0])
                        return 1;
                    else
                        return 0;
                });
            }

            $scope.loading = false;
            $scope.offset += data["results"].length;
            if ($scope.offset >= data["total"])
                $scope.all_loaded = true;
        });
    };

    $scope.applyResults = function(results) {
        // Group results by day
        var results_dict = {}

        $scope.sortArrayByDate(results);

        for (var i = 0; i < results.length; i++) {
            var d = new Date(Date.parse(results[i].published));
            d.setUTCHours(0);d.setUTCMinutes(0);d.setUTCSeconds(0);d.setUTCMilliseconds(0);
            var d_string = d.toISOString();
            if (!(d_string in results_dict))
                results_dict[d_string] = [];

            results_dict[d_string].push(results[i]);
        };


        // Merge results
        for (var date in results_dict) {
            if (!results_dict.hasOwnProperty(date)) continue;

            // If the key exists, merge it
            if (date in $scope.results) {
                $scope.results[date] = $scope.results[date].concat(results_dict[date]);
                $scope.sortArrayByDate($scope.results[date]);
            }
            else {
                $scope.results[date] = results_dict[date];
            }
        }

        var results_array = [];
        for (var key in $scope.results) {
            if (!$scope.results.hasOwnProperty(key)) continue;
            results_array.push({ 'published': key, 'articles' : $scope.results[key]});
        }

        $scope.sortArrayByDate(results_array);
        $scope.results_array = results_array;
    };

    $scope.sortArrayByDate = function(array) {
        array.sort(function (a, b) {
           if (a.published < b.published)  return 1;
           if (a.published > b.published)  return -1;
           return 0;
        });
    };
});
