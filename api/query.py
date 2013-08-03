from cornice import Service
import settings
from pysolarized import solr
from pysolarized import from_solr_date

news_query = Service(name="news_query", path="/news/query/", description="Returns news matching the query")

@news_query.get()
def get_news(request):
    if "q" not in request.GET:
        return { "error" : "Missing q query parameter." }


    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    results = solr_int.query(request.GET["q"], sort=["published desc"])

    if results is None:
        return { "error" : "Failed to connect to news search server." }

    documents = []
    for doc in results.documents:
        document = { "published" : str(from_solr_date(doc["published"]).isoformat()) + "Z", "link":doc["source_url"],
                "source" : doc["source"] }

        if "author" in doc and doc["author"] is not None:
            document["author"] = doc["author"]

        if u"title" in results.highlights[doc["id"]]:
            document["title"] = results.highlights[doc["id"]][u"title"]
        else:
            document["title"] = doc["title"]

        if u"content" in results.highlights[doc["id"]]:
            document["snippet"] = results.highlights[doc["id"]][u"content"]

        documents.append(document)

    return { "results" : documents}
