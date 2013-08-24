from cornice import Service
import settings
from pysolarized import solr
from pysolarized import from_solr_date

news_query = Service(name="news_query", path="/news/query/", description="Returns news matching the query")

PAGE_SIZE = 30

@news_query.get()
def get_news(request):
    if "q" not in request.GET:
        return { "error" : "Missing q query parameter." }

    start_index = 0
    if "offset" in request.GET:
        start_index = int(request.GET["offset"])

    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    results = solr_int.query(request.GET["q"], sort=["published desc"], start=start_index, rows=PAGE_SIZE)

    if results is None:
        return { "error" : "Failed to connect to news search server." }

    documents = []
    for doc in results.documents:
        document = {"id": doc["id"],
                    "published": str(from_solr_date(doc["published"]).isoformat()) + "Z",
                    "link": doc["source_url"],
                    "source": doc["source"]}

        if "author" in doc and doc["author"] is not None:
            document["author"] = doc["author"]

        if u"title" in results.highlights[doc["id"]]:
            document["title"] = results.highlights[doc["id"]][u"title"]
        else:
            document["title"] = doc["title"]

        if u"content" in results.highlights[doc["id"]]:
            document["snippet"] = results.highlights[doc["id"]][u"content"]

        documents.append(document)
    
    r = {"results": documents}

    if results.facets is not None:
        r["facets"] = {}
        if "published" in results.facets:

            # Remove "before" or "after" facet fields if they have 0 results
            published_facets = [ facet for facet in results.facets["published"] \
                    if not ((facet[0] == "before" and facet[1] == 0) or (facet[0] == "after" and facet[1] == 0))]
            r["facets"]["published"] = published_facets
        if "source" in results.facets:
            r["facets"]["source"] = results.facets["source"]

    # Calculate pagination information
    r["offset"] = start_index
    r["total"] = results.results_count 
    return r
