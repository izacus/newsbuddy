from cornice import Service
import db
from db.news import NewsItem
import settings
from pysolarized import solr
from pysolarized import from_solr_date
from sqlalchemy.orm.exc import NoResultFound

news_query = Service(name="news_query", path="/news/query/", description="Returns news matching the query")
latest = Service(name="latest_news", path="/news/latest/", description="Returns latest collected news")
details = Service(name="news_details", path="/news/detail/", description="Returns detail about a news document")

PAGE_SIZE = 30


@latest.get()
def get_latest(request):
    results = query_for("*")
    # Hide facets and fix count
    del results[u"facets"]
    del results[u"offset"]
    results[u"total"] = len(results[u"results"])
    return results

@details.get()
def get_details(request):
    if u"id" not in request.GET:
        return {u"error": u"Missing id query parameter."}

    id = request.GET["id"]
    db_session = db.news.get_db_session()

    try:
        item = db_session.query(NewsItem).filter(NewsItem.id == id).one()
    except NoResultFound:
        return {u"error": u"Document matching id was not found."}

    return {
        u"id": item.id,
        u"title": item.title,
        u"author": item.author,
        u"published": str(item.published.isoformat()) + "Z",
        u"source": item.source,
        u"link": item.source_url
    }

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
            filters[u"published"] = "[" + request.GET[u"published"] + " TO " + request.GET[u"published"] + "+1DAYS]"
        if u"source" in request.GET:
            filters[u"source"] = request.GET[u"source"]

    return query_for(request.GET[u"q"], start_index=start_index, filters=filters)


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
