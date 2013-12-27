angular.module("NewsBuddy").controller("SearchController", ["$scope", "$http", "$location", function($scope, $http, $location) {

    var MAX_LATEST_NEWS = 500;

    $scope.query = null;

    $scope.clearSearch = function() {
        $scope.offset = 0;
        $scope.results = {};

        // Clear filters only if there's a new query
        if ($scope["old_query"] == undefined || $scope.old_query != $scope.query)
            $scope.search_filters = {};

        $scope.old_query = $scope.query;
        $scope.results_array = [];      // Array to show results
        $scope.sources = null;
        $scope.publish_dates = null;
        $scope.all_loaded = false;
    };

    $scope.search = function() {
        if (!$scope.query)
            return;

        $('#no-results').show();
        $scope.clearSearch();
        $scope.loadPage();
    };

    $scope.loadInfinite = function() {
        if ($scope.query) {
            $scope.loadPage();
        }
        else {
            $scope.loadLatestNews();
        }
    }

    $scope.loadLatestNews = function() {
        if ($scope.loading || $scope.offset > MAX_LATEST_NEWS)
            return;

        $scope.loading = true;
        $scope.all_loaded = false;
        $http.get('/v1/news/latest/?offset=' + $scope.offset).success(function data(data) {
            $scope.loading = false;
            applyResults(data["results"]);
            $scope.offset += data["results"].length;
        });
    }

    $scope.loadPage = function()
    {
        if ($scope.loading)
            return;

        $scope.loading = true;
        var path = '/v1/news/query/'
        var url = path + '?offset=' + $scope.offset + '&q=' + $scope.query;
        for (var filter in $scope.search_filters) {
            if ($scope.search_filters.hasOwnProperty(filter)) {
                url += "&" + filter + "=" + encodeURIComponent($scope.search_filters[filter]);
            }
        }

        $location.hash($scope.query);
        $http.get(url).success(function data(data) {
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

            /* Must add new element - just altering the old one doesn't update
             * the feed subscribe UI in Firefox. Also, Firefox doesn't remove
             * old entries from the UI when we delete the <link>.
             *
             * Chrome + RSS subscription extension ignore this altogether.
             *
             * We check if there is an existing matching element to prevent
             * cluttering Firefox too much. */
            var atom_url = path + '?q=' + $scope.query;
            var exists = 0;

            var links = $('head link[rel="alternate"]');
            links.each(function(index) {
                if($(this).attr('href') === atom_url) {
                    exists = 1;
                }
            });
            links.remove();

            if (!exists) {
                $('head').append($('<link>', {
                    'href': atom_url,
                    'rel': 'alternate',
                    'type': 'application/atom+xml',
                    'title': $scope.query + ' - Novičar'}));
            }
        });
    };

    /**
     * Adds a filter to list and restarts query
     * @param field
     * @param value
     */
    $scope.filter = function(field, value) {
        $scope.clearSearch();
        if (value === null) {
            delete $scope.search_filters[field];
        }
        else {
            if (field === "published" && value === "Prej")
                value = "before";

            $scope.search_filters[field] = value;
        }

        $scope.loadPage();
    };

    $scope.processSuggestions = function(parsedResponse) {
        console.info(parsedResponse);
        return parsedResponse["suggestions"];
    }

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
                var sourceFacets = facets["source"];
                // Sort sources by number of hits descending
                sourceFacets.sort(function (a, b) {
                    return b[1] - a[1];
                });

                $scope.sources = sourceFacets;
            }

        if (facets["published"] != null) {
            var publishedFacets = facets["published"];
            publishedFacets.sort(function (a,b) {
                if (a[0] > b[0])
                    return -1;
                else if (a[0] < b[0])
                    return 1;
                else
                    return 0;
            });

            if (publishedFacets.length > 0 && publishedFacets[0][0] == "before")
            {
                publishedFacets[0][0] = "Prej";     // Rename "before" Solr marker to Slovenian "Prej"
                // This moves the marker to last place where it should be
                var element = publishedFacets.shift();
                publishedFacets.push(element);
            }

            $scope.publish_dates = publishedFacets;
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

    $scope.$on("newsbuddy:autocomplete:selected", function(e) {
        $scope.search();
        $scope.$digest();
    });

    if ($location.hash())
    {
        $scope.query = $location.hash();
        $scope.search();
    }
    else
    {
        $scope.loadLatestNews();
    }
}]);
