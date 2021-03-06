from api import app
from db.cache import get_cache
from pysolarized import solr, from_solr_date
from flask import request
import settings

cache = get_cache()


@app.route("/v1/news/related/")
def get_related():
    news_id = request.args.get(u"id", None)
    if not news_id:
        return {"error": "missing id parameter"}
    return get_related_id(news_id)


@app.route("/v1/news/related/<string:news_id>/")
def get_related_id(news_id):
    return build_related(news_id)

@cache.cache_on_arguments()
def build_related(id):
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    results = solr_int.more_like_this("id:%s" % id, ["title", "content"], ["id",
                                                                           "title",
                                                                           "published",
                                                                           "source",
                                                                           "source_url",
                                                                           "author",
                                                                           "score"])

    if results is None:
        return {u"error": u"Failed to connect to news search server."}

    documents = []
    for doc in results.documents:
        if "score" in doc and float(doc["score"]) < 0.1:
            continue

        document = {u"id": doc["id"],
                    u"published": str(from_solr_date(doc["published"]).isoformat()) + "Z",
                    u"link": doc["source_url"],
                    u"source": doc["source"]}

        if u"author" in doc and doc[u"author"] is not None:
            document[u"author"] = doc["author"]
        document[u"title"] = doc["title"]

        if u"score" in doc:
            document[u"score"] = doc["score"]

        documents.append(document)

    r = {u"results": documents}
    return r