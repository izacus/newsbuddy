from cornice import Service
import settings
from pysolarized import solr
from pysolarized import from_solr_date

news_query = Service(name="news_query", path="/news/query/", description="Returns news matching the query")
latest = Service(name="latest_news", path="/news/latest/", description="Returns latest collected news")

PAGE_SIZE = 30


@latest.get()
def get_latest(request):
    results = query_for("*")
    # Hide facets and fix count
    del results[u"facets"]
    del results[u"offset"]
    results[u"total"] = len(results[u"results"])
    return results


@news_query.get()
def get_news(request):
    if u"q" not in request.GET:
        return {u"error": u"Missing q query parameter."}
    start_index = 0
    if u"offset" in request.GET:
        start_index = int(request.GET[u"offset"])

    filters = None
    if u"published" in request.GET or u"source" in request.GET:
        filters = {}
        if u"published" in request.GET:
            filters[u"published"] = request.GET[u"published"]
        if u"source" in request.GET:
            filters[u"source"] = request.GET[u"source"]

    return query_for(request.GET["q"], start_index=start_index, filters=filters)


def query_for(query, start_index=0, filters=None):
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    results = solr_int.query(query, sort=["published desc"], start=start_index, rows=PAGE_SIZE, filters=filters)

    if results is None:
        return {u"error": u"Failed to connect to news search server."}

    documents = []
    for doc in results.documents:
        document = {u"id": doc["id"],
                    u"published": str(from_solr_date(doc["published"]).isoformat()) + "Z",
                    u"link": doc["source_url"],
                    u"source": doc["source"]}

        if u"author" in doc and doc[u"author"] is not None:
            document[u"author"] = doc["author"]

        if u"title" in results.highlights[doc["id"]]:
            document[u"title"] = results.highlights[doc["id"]]["title"][0]
        else:
            document[u"title"] = doc["title"]

        if u"content" in results.highlights[doc["id"]]:
            document[u"snippet"] = results.highlights[doc["id"]]["content"]

        documents.append(document)
    
    r = {u"results": documents}

    if results.facets is not None:
        r[u"facets"] = {}
        if "published" in results.facets:

            # Remove "before" or "after" facet fields if they have 0 results
            published_facets = [facet for facet in results.facets["published"]
                                if not ((facet[0] == "before" and facet[1] == 0) or (facet[0] == "after" and facet[1] == 0))]
            r[u"facets"][u"published"] = published_facets
        if "source" in results.facets:
            r[u"facets"][u"source"] = results.facets["source"]

    # Calculate pagination information
    r[u"offset"] = start_index
    r[u"total"] = results.results_count
    return r
