var newsBuddy = angular.module('NewsBuddy', ['infinite-scroll']);

newsBuddy.controller('SearchController', function($scope, $http) {

    $scope.offset = 0;
    $scope.all_loaded = false;

    $scope.search = function() {
        $scope.offset = 0;
        $scope.results = []; 
        $scope.sources = null;
        $scope.publish_dates = null;
        $scope.all_loaded = false;
        $scope.loadPage();
    }

    $scope.loadPage = function()
    {
        console.info($scope)
        if ($scope.loading)
            return;

        if (!$scope.query)
            return;

        $scope.loading = true;
        $http.get('/news/query/?offset=' + $scope.offset + '&q=' + $scope.query).success(function data(data) {
            $scope.results.push.apply($scope.results, data["results"]);

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

    }
});
