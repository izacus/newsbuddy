import logging
import scrapers
import settings
import db.news
from pysolarized import to_solr_date
from pysolarized import solr

def dispatch_to_solr(news):
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    # Build documents for solr dispatch
    docs = []
    for news_item in news:
        doc = { "id" : news_item["id"], "title" : news_item["title"],
                "source" : news_item["source"], "language" : news_item["language"],
                "source_url" : news_item["source_url"], "content" : news_item["text"],
                "published" : to_solr_date(news_item["published"]) }
        docs.append(doc)

    solr_int.add(docs)
    solr_int.commit()
    print "Dispatch done."

if __name__ == "__main__":
    logging.basicConfig()

    existing_ids = db.news.get_latest_ids(1000)
    news = scrapers.scrape_news(existing_ids)
    db.news.store_news(news)

    if settings.SOLR_ENDPOINT_URLS is not None:
        dispatch_to_solr(news)
