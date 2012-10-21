from cornice import Service
import settings
from solr import solr

news_query = Service(name="news_query", path="/news/query/", description="Returns news matching the query")

@news_query.get()
def get_news(request):
    if "q" not in request.GET:
        return { "error" : "Missing q query parameter." }


    solr_int = solr.SolrInterface(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    results = solr_int.query(request.GET["q"], sort=["published desc"])

    if results is None:
        return { "error" : "Failed to connect to news search server." }

    return { "results" : [doc for doc in results.documents]}
