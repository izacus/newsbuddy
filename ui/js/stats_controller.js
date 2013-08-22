var newsBuddy = angular.module('NewsBuddy', []);
google.load("visualization", "1", { packages: ["corechart"]});


newsBuddy.controller('StatsController', function($scope, $http) {
    $scope.stats = { "total_news" : 0, "news_today": 0 };

    $http.get('/news/stats/').success(function data(data) {
        $scope.stats = data;


        var sources = data["total_by_source"];
        var sources_today = data["total_by_source_today"];

        var labels = [ null ];
        var sources_data = [ null ];

        for (var item in sources) {
            if (sources.hasOwnProperty(item)) {
                labels.push(item);
                sources_data.push(sources[item]);
            }
        }

        var labels_today = [ null ];
        var sources_today_data = [ null ];
        for (var item in sources_today) {
            if (sources.hasOwnProperty(item)) {
                labels_today.push(item);
                sources_today_data.push(sources_today[item]);
            }
        }

        // Draw data chart
        var sources_data = google.visualization.arrayToDataTable([
            labels, sources_data
        ]);

        var sources_today_data = google.visualization.arrayToDataTable([
            labels_today, sources_today_data
        ]);
        var options = {
            hAxis: { title: "Novic" },
            tooltip: { showColorCode: true }
        };

        var sources_chart = new google.visualization.BarChart(document.getElementById('news-by-source'));
        sources_chart.draw(sources_data, options);

        var sources_today_chart = new google.visualization.BarChart(document.getElementById('news-by-source-today'));
        sources_today_chart.draw(sources_today_data, options);
    });
});