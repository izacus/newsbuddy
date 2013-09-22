
function DetailsController($scope, $routeParams, $http) {
    $scope.loading = true;

    var details_url = '/news/detail/?id=' + $routeParams.resultId;
    var related_url = '/news/related/?id=' + $routeParams.resultId;

    $http.get(details_url).success(function data(data) {
        $scope.news_item = data;
        console.info(data);
    })

    $http.get(related_url).success(function data(data){
        $scope.loading = false;
        $scope.related_news = data.results;
    });
}