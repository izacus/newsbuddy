function SearchResultsController($scope, $http) {
    $http.get('/news/query/?q=janez').success(function data(data) {
        $scope.results = data["results"];
        console.info(data);
    });
}
