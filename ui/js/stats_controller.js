google.load("visualization", "1", { packages: ["corechart"]});
angular.module("NewsBuddy").controller("StatsController", ["$scope", "$http", function($scope, $http) {
    $scope.stats = { "total_news" : 0, "news_today": 0 };

    $http.get('/v1/news/stats/').success(function data(data) {
        $scope.stats = data;


        var sources = data["total_by_source"];
        var sources_today = data["total_by_source_today"];
        var news_by_day = data["news_by_day"]

        var news_by_day_data = new google.visualization.DataTable();
        news_by_day_data.addColumn('date', "Dan");
        news_by_day_data.addColumn('number', "Stevilo");

        // Sort data entries by date
        var date_keys = []
        for (var item in news_by_day) {
            if (news_by_day.hasOwnProperty(item)) {
                date_keys.push(item);
            }
        }

        date_keys.sort();
        for (var i = 0; i < date_keys.length; i++) {
            var item = date_keys[i];
            var date = new Date(Date.parse(item));
            news_by_day_data.addRow( [ date, news_by_day[item]] );
        }


        var labels = [];
        var sources_data = [];

        for (var item in sources) {
            if (sources.hasOwnProperty(item)) {
                labels.push(item);
                sources_data.push(sources[item]);
            }
        }

        var labels_today = [ ];
        var sources_today_data = [ ];
        for (var item in sources_today) {
            if (sources.hasOwnProperty(item)) {
                labels_today.push(item);
                sources_today_data.push(sources_today[item]);
            }
        }

        var sources_data = google.visualization.arrayToDataTable([
            labels, sources_data
        ]);

        var sources_today_data = google.visualization.arrayToDataTable([
            labels_today, sources_today_data
        ]);
        var options = {
            hAxis: { title: "Novic" },
            tooltip: { showColorCode: true },
            backgroundColor: "#f9f9f9"
        };

        var news_by_day_chart = new google.visualization.AreaChart(document.getElementById('news-by-day'));
        news_by_day_chart.draw(news_by_day_data, { "legend.position": "none", isStacked: true, backgroundColor: "#f9f9f9" });

        var sources_chart = new google.visualization.BarChart(document.getElementById('news-by-source'));
        sources_chart.draw(sources_data, options);

        var sources_today_chart = new google.visualization.BarChart(document.getElementById('news-by-source-today'));
        sources_today_chart.draw(sources_today_data, options);
    });
}]);