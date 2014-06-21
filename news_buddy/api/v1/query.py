import datetime
from api import app
import db
from flask import request
from flask.ext.api.decorators import set_renderers
from atom_renderer import AtomXMLRenderer, AtomRenderer
from flask.ext.api.renderers import JSONRenderer, BrowsableAPIRenderer
from requests import Session
import settings
from pysolarized import solr
from pysolarized import from_solr_date
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound

from db.news import NewsItem
from db.tags import Tag         # Has to be imported for proper relation management
from db.cache import get_cache
import mining.summarizer
import mining.entity_extractor

req_session = Session()

summarizer = mining.summarizer.Summarizer()
entity_extractor = mining.entity_extractor.EntityExtractor()
cache = get_cache()

PAGE_SIZE = 30

@app.route("/v1/news/latest/")
@set_renderers(BrowsableAPIRenderer, JSONRenderer, AtomXMLRenderer, AtomRenderer)  # Note the order is important
def get_latest():
    """
    Renders latest news
    """
    offset = request.data.get(u'offset', 0)
    result = build_latest_news(offset)
    if u"error" in result:
        build_latest_news.invalidate()
    return result


@app.route("/v1/news/detail/", methods=["GET"])
def get_details():
    """
    Renders details for a certain news item
    """
    news_id = request.args.get(u"id", None)
    if not news_id:
        return {u"error": u"Missing id query parameter."}
    return get_details_id(news_id)


@app.route("/v1/news/detail/<string:news_id>/", methods=["GET"])
def get_details_id(news_id):
    """
    Renders details for a certain news item
    """
    return build_details(news_id)


@app.route("/v1/news/suggest/query/", methods=["GET"])
def get_query_suggestions():
    query = request.args.get(u"q", None)
    if not query:
        return {u"error": u"Missing q query parameter."}

    return build_query_suggestions(query)

@app.route("/v1/news/query/", methods=["GET"])
@set_renderers(BrowsableAPIRenderer, JSONRenderer, AtomXMLRenderer, AtomRenderer)  # Note the order is important
def get_news():
    query = request.args.get(u"q", None)
    if not query:
        return {u"error": u"Missing q query parameter."}

    start_index = request.args.get(u"offset", 0)

    filters = None
    if u"published" in request.args or u"source" in request.args:
        filters = {}
        if u"published" in request.args:
            if request.args[u"published"] == u"before":
                now = datetime.datetime.utcnow()
                up_to_date = datetime.date(year=now.year, month=now.month - 1, day=1)
                filters[u"published"] = "[* TO " + up_to_date.strftime("%Y-%m-%dT00:00:00Z") + "]"
            else:
                filters[u"published"] = "[" + request.args[u"published"] + " TO " + request.args[u"published"] + "+1DAYS]"
        if u"source" in request.args:
            filters[u"source"] = request.args[u"source"]

    results = query_for(query, start_index, filters, False)
    if results is not None:
        results["query"] = query

    return results

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


@cache.cache_on_arguments()
def build_details(id):
    db_session = db.get_db_session()
    try:
        item = db_session.query(NewsItem).filter(NewsItem.id == id).options(subqueryload(NewsItem.tags)).one()
    except NoResultFound:
        return {u"error": u"Document matching id was not found."}
    finally:
        db_session.close()

    return {
        u"id": item.id,
        u"title": item.title,
        u"author": item.author,
        u"published": str(item.published.isoformat()) + "Z",
        u"source": item.source,
        u"link": item.source_url,
        u"content": item.content,
        u"tags": [(tag.tag_name, tag.tag_type) for tag in item.tags]
    }


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
