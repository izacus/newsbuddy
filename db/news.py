import settings
from sqlalchemy import Column, String, UnicodeText, DateTime, Unicode, create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news"

    id = Column(String, primary_key=True)
    title = Column(UnicodeText)
    published = Column(DateTime(timezone=True))
    source = Column(Unicode)
    source_url = Column(Unicode)
    content = Column(UnicodeText)

def create_news_db(engine):
    Base.metadata.create_all(engine)

def get_latest_ids(limit=500):
    db_engine = create_engine(settings.DB_CONNECTION_STRING)
    Session = sessionmaker(bind=db_engine)
    db_sesion = Session()
    existsing_ids = {id[0] for id in db_sesion.query(NewsItem.id).order_by(desc(NewsItem.published))[:100]}
    return existsing_ids

def store_news(news):
    # Attempt to create database if it doesn't exist
    db_engine = create_engine(settings.DB_CONNECTION_STRING)
    create_news_db(db_engine)
    Session = sessionmaker(bind=db_engine)

    db_session = Session()
    ids = [news_item["id"] for news_item in news]
    existing_ids = {id[0] for id in db_session.query(NewsItem.id).filter(NewsItem.id.in_(ids)).all()}

    count = 0
    for news_item in news:
        if news_item["id"] in existing_ids:
            continue
        db_item = NewsItem(id=news_item["id"], title=news_item["title"],
                           source=news_item["source"], source_url=news_item["source_url"],
                           published=news_item["published"], content=news_item["text"])
        db_session.merge(db_item)
        count += 1

    db_session.commit()
    print "Added ", count,  " new items."