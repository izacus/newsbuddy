function SearchResultsController($scope, $http) {

    $scope.search = function() {
        $scope.loading = true;
        $scope.results = null; 
        $http.get('/news/query/?q=' + $scope.query).success(function data(data) {
            $scope.results = data["results"];

            if (data["facets"]["source"] != null) {
                $scope.sources = data["facets"]["source"];
                // Sort sources by number of hits descending
                $scope.sources.sort(function (a, b) {
                    return b[1] - a[1];
                });
            }
            else
                $scope.sources = null;
            
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
            else
                $scope.publish_dates = null;

            $scope.loading = false;
        });
    }
}
