import settings
import pytz
from sqlalchemy import Column, String, UnicodeText, DateTime, Unicode, create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news"

    id = Column(String(128), primary_key=True)
    title = Column(UnicodeText)
    author = Column(UnicodeText)
    published = Column(DateTime(timezone=False))
    source = Column(UnicodeText)
    source_url = Column(UnicodeText)
    content = Column(UnicodeText)

def create_news_db(engine):
    Base.metadata.create_all(engine)

def get_db_session():
    db_engine = create_engine(settings.DB_CONNECTION_STRING)
    create_news_db(db_engine)
    Session = sessionmaker(bind=db_engine)
    return Session()

def get_latest_ids(limit=500):
    db_sesion = get_db_session()
    existsing_ids = set(id[0] for id in db_sesion.query(NewsItem.id).order_by(desc(NewsItem.published))[:100])
    return existsing_ids

def store_news(news):
    db_session = get_db_session()
    ids = [news_item["id"] for news_item in news]
    existing_ids = set(id[0] for id in db_session.query(NewsItem.id).filter(NewsItem.id.in_(ids)).all())

    count = 0
    for news_item in news:
        if news_item["id"] in existing_ids:
            continue

        existing_ids.add(news_item["id"])

        db_item = NewsItem(id=news_item["id"], title=news_item["title"],
                           source=news_item["source"], source_url=news_item["source_url"],
                           published=news_item["published"].astimezone(pytz.utc).replace(tzinfo=None), content=news_item["text"], author=news_item["author"])
        db_session.add(db_item)
        count += 1

    db_session.commit()

def get_news():
    db_session = get_db_session()
    return db_session.query(NewsItem).yield_per(50)
