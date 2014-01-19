from cornice import Service
import datetime
import db
from requests import Session
import settings
from pysolarized import solr
from pysolarized import from_solr_date
from sqlalchemy.orm.exc import NoResultFound

from db.news import NewsItem
from db.cache import get_cache
from api.v1.atom_renderer import AtomRenderer
import mining.summarizer
import mining.entity_extractor


req_session = Session()

news_query = Service(name="news_query", path="/v1/news/query/", description="Returns news matching the query")
latest = Service(name="latest_news", path="/v1/news/latest/", description="Returns latest collected news")
details = Service(name="news_details", path="/v1/news/detail/", description="Returns detail about a news document")
query_suggest = Service(name="news_query_suggest", path="/v1/news/suggest/query", description="Returns query suggestions")

summarizer = mining.summarizer.Summarizer()
entity_extractor = mining.entity_extractor.EntityExtractor()
cache = get_cache()

PAGE_SIZE = 30


@latest.get(accept='application/json', renderer='json')
@latest.get(accept=AtomRenderer.acceptable, renderer='atom')
def get_latest(request):
    offset = 0
    if u"offset" in request.GET:
        offset = int(request.GET["offset"])

    result = build_latest_news(offset)
    if u"error" in result:
        build_latest_news.invalidate()
    return result

@cache.cache_on_arguments()
def build_latest_news(offset):
    results = query_for("*", offset, None, True)

    if u"error" in results:
        return results

    # Hide facets and fix count
    del results[u"facets"]
    del results[u"offset"]
    results[u"total"] = len(results[u"results"])

    # Summarize results
    for result in results[u"results"]:
        content = result[u"content"]
        summary = summarizer.summarize(content)
        del result[u"content"]
        result[u"snippet"] = summary

    return results

@details.get()
def get_details(request):
    if u"id" not in request.GET:
        return {u"error": u"Missing id query parameter."}

    id = request.GET["id"]
    return build_details(id)

@cache.cache_on_arguments()
def build_details(id):
    db_session = db.news.get_db_session()
    try:
        item = db_session.query(NewsItem).filter(NewsItem.id == id).one()
    except NoResultFound:
        return {u"error": u"Document matching id was not found."}

    tags = entity_extractor.tag(item.content)

    return {
        u"id": item.id,
        u"title": item.title,
        u"author": item.author,
        u"published": str(item.published.isoformat()) + "Z",
        u"source": item.source,
        u"link": item.source_url,
        u"content": item.content,
        u"tags": tags
    }

@query_suggest.get()
def get_query_suggestions(request):
    if u"q" not in request.GET:
        return {u"error": u"Missing q query parameter."}
    query = request.GET[u"q"]
    return build_query_suggestions(query)

@cache.cache_on_arguments()         # TODO TODO: Prevent caching of Solr error responses
def build_query_suggestions(query):
    suggest_url = settings.SOLR_ENDPOINT_URLS[settings.SOLR_DEFAULT_ENDPOINT] + "suggest"
    parameters = {u"q": query, u"wt": u"json"}
    result = req_session.post(suggest_url, data=parameters)
    result_json = result.json()
    suggestion_data = result_json["spellcheck"]["suggestions"]

    if len(suggestion_data) == 0:
        return {u"suggestions": [], u"startOffset": 0, u"endOffset": 0, u"fieldSuggestion": None}

    start_offest = suggestion_data[1]["startOffset"]
    end_offset = suggestion_data[1]["endOffset"]
    suggestions = suggestion_data[1]["suggestion"]
    field_fill = suggestion_data[3]

    return {u"suggestions": suggestions, u"startOffset": start_offest, u"endOffset": end_offset, u"fieldSuggestion": field_fill}


@news_query.get(accept='application/json', renderer='json')
@news_query.get(accept=AtomRenderer.acceptable, renderer='atom')
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
            if request.GET[u"published"] == u"before":
                now = datetime.datetime.utcnow()
                up_to_date = datetime.date(year=now.year, month=now.month - 1, day=1)
                filters[u"published"] = "[* TO " + up_to_date.strftime("%Y-%m-%dT00:00:00Z") + "]"
            else:
                filters[u"published"] = "[" + request.GET[u"published"] + " TO " + request.GET[u"published"] + "+1DAYS]"
        if u"source" in request.GET:
            filters[u"source"] = request.GET[u"source"]

    return query_for(request.GET[u"q"], start_index, filters, False)

@cache.cache_on_arguments()         # TODO TODO: Prevent caching of Solr error responses
def query_for(query, start_index, filters, with_content):
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

        if with_content:
            document[u"content"] = doc["content"]

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
