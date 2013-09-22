import logging
import settings
import db.news
import pytz
from pysolarized import to_solr_date
from pysolarized import solr

if __name__ == "__main__":
    logging.basicConfig()
    
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    solr_int.deleteAll()
    # Now iterate over news
    docs = []
    count = 0
    for news_item in db.news.get_news():
        doc = {u"id": news_item.id, u"title": news_item.title,
               u"source": news_item.source, u"language": u"si",
               u"source_url": news_item.source_url, u"content": news_item.content,
               u"published": to_solr_date(news_item.published.replace(tzinfo=pytz.utc))}

        if news_item.author is not None:
            doc[u"author"] = news_item.author

        solr_int.add(doc)
        count += 1

    solr_int.commit()

    print "Dispached " + str(count) + " documents to solr. "
