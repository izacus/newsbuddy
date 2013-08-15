var newsBuddy = angular.module('NewsBuddy', []);
google.load("visualization", "1", { packages: ["corechart"]});


newsBuddy.controller('StatsController', function($scope, $http) {
    $scope.stats = { "total_news" : 0, "news_today": 0 };

    $http.get('/news/stats/').success(function data(data) {
        $scope.stats = data;


        var sources = data["total_by_source"];
        var labels = [ null ]
        var data = [ null ]

        for (var item in sources) {
            if (sources.hasOwnProperty(item)) {
                labels.push(item);
                data.push(sources[item]);
            }
        }


        // Draw data chart
        var data = google.visualization.arrayToDataTable([
            labels, data
        ]);

        var options = {
            hAxis: { title: "Novic" },
            tooltip: { showColorCode: true }
        };

        var chart = new google.visualization.BarChart(document.getElementById('news-by-source'));
        chart.draw(data, options);
    });
});