var newsBuddy = angular.module('NewsBuddy', ['infinite-scroll']);

$(document).ready(function () {
   $('#no-results').hide();
});

newsBuddy.controller('SearchController', function($scope, $http) {

    $scope.clearSearch = function() {
        $scope.offset = 0;
        $scope.results = {};
        $scope.results_array = [];      // Array to show results
        $scope.sources = null;
        $scope.publish_dates = null;
        $scope.all_loaded = false;
    };

    $scope.search = function() {
        $scope.clearSearch();
        $scope.loadPage();
    };

    $scope.loadLatestNews = function() {
        $scope.loading = true;
        $http.get('/news/latest/').success(function data(data) {
            $scope.loading = false;
            $scope.all_loaded = true;
            applyResults(data["results"]);
        });
    }

    $scope.loadPage = function()
    {
        if ($scope.loading)
            return;

        if (!$scope.query)
            return;

        $scope.loading = true;
        $http.get('/news/query/?offset=' + $scope.offset + '&q=' + $scope.query).success(function data(data) {

            if (!data["results"]) {
                $scope.loading = false;
                return;
            }

            applyResults(data["results"]);
            renderFacets(data["facets"]);

            $scope.loading = false;
            $scope.offset += data["results"].length;
            if ($scope.offset >= data["total"])
                $scope.all_loaded = true;
        });
    };

    /**
     * Adds new results to result arrays and triggers rendering
     * @param results
     */
    var applyResults = function(results) {
        // Add results to result dictionary
        sortArrayByDate(results);
        for (var i = 0; i < results.length; i++) {
            var date = isoDateToMidnight(results[i].published);
            if (!(date in $scope.results))
                $scope.results[date] = [];

            $scope.results[date].push(results[i]);
        }

        // Now update results array. We need to make sure we only add items to appropriate part to prevent full re-render
        for (var date in $scope.results)
        {
            // Find array item in result array
            var item = $.grep($scope.results_array, function(i) { return i.published === date; });
            if (item.length == 0) {
                $scope.results_array.push({ 'published': date, 'articles': $scope.results[date]});
            }
            else {
                // Merge subarrays if the subarray already exists
                var article_array = item[0].articles.slice();
                for (var i = 0; i < $scope.results[date].length; i++) {
                    var result = $scope.results[date][i];
                    if (!documentInArray(article_array, result.id))
                        article_array.push(result);
                }
                item[0].articles = article_array;
            }

        }
    };

    var documentInArray = function(array, document_id) {
        for (var i = 0; i < array.length; i++) {
            if (array[i].id === document_id)
                return true;
        }
        return false;
    }

    var isoDateToMidnight = function(date) {
        var d = new Date(Date.parse(date));
        d.setUTCHours(0);d.setUTCMinutes(0);d.setUTCSeconds(0);d.setUTCMilliseconds(0);
        return d.toISOString();
    }

    var renderFacets = function(facets) {
        if (facets["source"] != null) {
                $scope.sources = facets["source"];
                // Sort sources by number of hits descending
                $scope.sources.sort(function (a, b) {
                    return b[1] - a[1];
                });
            }

        if (facets["published"] != null) {
            $scope.publish_dates = facets["published"]
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
    }

    var sortArrayByDate = function(array) {
        array.sort(function (a, b) {
           if (a.published < b.published)  return 1;
           if (a.published > b.published)  return -1;
           return 0;
        });
    };

    $scope.clearSearch();
    $scope.loadLatestNews();
});
