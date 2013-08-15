import logging
import requests
import scrapers
import settings
import db.news
from pysolarized import to_solr_date
from pysolarized import solr

logger = logging.getLogger("newsbuddy")

def dispatch_to_solr(news):
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    # Build documents for solr dispatch
    docs = []
    for news_item in news:
        doc = { "id" : news_item["id"], "title" : news_item["title"],
                "source" : news_item["source"], "language" : news_item["language"],
                "source_url" : news_item["source_url"], "content" : news_item["text"],
                "published" : to_solr_date(news_item["published"]) }
        
        if news_item["author"] is not None:
            doc["author"] = news_item["author"]

        docs.append(doc)

    solr_int.add(docs)
    solr_int.commit()
    print "Dispatch done."

if __name__ == "__main__":
    
    if settings.SENTRY_CONNECTION_STRING is not None:
        from raven import Client
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging
        logging.basicConfig(level=logging.WARN)
        client = Client(settings.SENTRY_CONNECTION_STRING)
        handler = SentryHandler(client)
        setup_logging(handler)
    else:
        logging.basicConfig(level=logging.DEBUG)

    try:
        existing_ids = db.news.get_latest_ids(2000)
        news = scrapers.scrape_news(existing_ids)
        db.news.store_news(news)
        if settings.SOLR_ENDPOINT_URLS is not None:
            dispatch_to_solr(news)
        requests.delete(settings.LOCAL_URL + "/news/stats/")
    except Exception as e:
        logger.error("Failed to process work packet!", exc_info=True)
