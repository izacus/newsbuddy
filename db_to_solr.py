import logging
import settings
import db.news
import pytz
from pysolarized import to_solr_date
from pysolarized import solr

if __name__ == "__main__":
    logging.basicConfig()
    
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    # Now iterate over news
    docs = []
    for news_item in db.news.get_news():
        doc = { "id" : news_item.id, "title" : news_item.title,
                "source" : news_item.source, "language" : "si",
                "source_url" : news_item.source_url, "content" : news_item.content,
                "published" : to_solr_date(news_item.published.replace(tzinfo=pytz.utc)) }    
        docs.append(doc)

    solr_int.add(docs)
    solr_int.commit()

    print "Dispached " + str(len(docs)) + " documents to solr. "
