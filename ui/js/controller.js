function SearchResultsController($scope, $http) {

    $scope.search = function() {
        console.info($scope.query)
        $http.get('/news/query/?q=' + $scope.query).success(function data(data) {
            $scope.results = data["results"];
            console.info(data);
        });
    }
}
