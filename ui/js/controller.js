function SearchResultsController($scope, $http) {

    $scope.search = function() {
        $scope.loading = true;
        $scope.results = null; 
        $http.get('/news/query/?q=' + $scope.query).success(function data(data) {
            $scope.results = data["results"];
            $scope.loading = false;
        });
    }
}
