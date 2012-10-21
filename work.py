from db.news import NewsItem, create_news_db
import scrapers
from solr import solr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def dispatch_to_solr(news):
    solr_int = solr.SolrInterface({ "SI" : "http://localhost:8983/solr/"}, "SI")
    # Build documents for solr dispatch
    docs = []
    for news_item in news:
        print u"Dispatching ", news_item["title"]
        doc = { "id" : news_item["id"], "title" : news_item["title"],
                "source" : news_item["source"], "language" : news_item["language"],
                "source_url" : news_item["source_url"], "content" : news_item["text"],
                "published" : solr.to_solr_date(news_item["published"]) }
        docs.append(doc)

    solr_int.add(docs)
    solr_int.commit()

def store_to_database(news):
    # Attempt to create database if it doesn't exist
    db_engine = create_engine("sqlite:///news.db")
    create_news_db(db_engine)
    Session = sessionmaker(bind=db_engine)

    db_session = Session()
    for news_item in news:
        db_item = NewsItem(id=news_item["id"], title=news_item["title"],
                           source=news_item["source"], source_url=news_item["source_url"],
                           published=news_item["published"], content=news_item["text"])
        db_session.add(db_item)
    db_session.commit()

if __name__ == "__main__":
    news = scrapers.scrape_news()
    store_to_database(news)
    dispatch_to_solr(news)
