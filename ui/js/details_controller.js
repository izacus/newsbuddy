angular.module("NewsBuddy").controller("DetailsController", ["$scope", "$routeParams", "$http", function($scope, $routeParams, $http) {
    $scope.loading = true;

    var details_url = '/v1/news/detail/?id=' + $routeParams.resultId;
    var related_url = '/v1/news/related/?id=' + $routeParams.resultId;

    $http.get(details_url).success(function data(data) {
        $scope.news_item = data;

        if (data["tags"]) {
            var tags = []
            for (var i = 0; i < data["tags"].length; i++) {
                tags.push({ "id": i, "word" : data["tags"][i][0], "tag": data["tags"][i][1]});
            }

            $scope.tags = tags;
        }
        else {
            $scope.tags = null;
        }

    })

    $http.get(related_url).success(function data(data){
        $scope.loading = false;
        $scope.related_news = data.results;
    });
}]);