import db
import pytz
from sqlalchemy import Column, String, UnicodeText, DateTime,  desc, Index

class NewsItem(db.Base):
    __tablename__ = "news"
    __table_args__ = (Index('news_published', 'published'), Index('news_source', 'source'), )

    id = Column(String(128), primary_key=True)
    title = Column(UnicodeText)
    author = Column(UnicodeText)
    published = Column(DateTime(timezone=False))
    source = Column(UnicodeText)
    source_url = Column(UnicodeText)
    content = Column(UnicodeText)
    raw_html = Column(UnicodeText)

    def __repr__(self):
        return unicode(self).encode("ascii", "replace")

    def __unicode__(self):
        return "< NewsItem: %s - %s >" % (self.title, self.id, )

def get_latest_ids(limit=500):
    db_sesion = db.get_db_session()
    existsing_ids = set(id[0] for id in db_sesion.query(NewsItem.id).order_by(desc(NewsItem.published))[:limit])
    db_sesion.close()
    return existsing_ids

def store_news(news):
    db_session = db.get_db_session()
    ids = [news_item["id"] for news_item in news]
    existing_ids = set(id[0] for id in db_session.query(NewsItem.id).filter(NewsItem.id.in_(ids)).all())

    count = 0

    stored_items = []
    for news_item in news:
        if news_item["id"] in existing_ids:
            continue

        existing_ids.add(news_item["id"])

        db_item = NewsItem(id=news_item["id"], title=news_item["title"],
                           source=news_item["source"], source_url=news_item["source_url"],
                           published=news_item["published"].astimezone(pytz.utc).replace(tzinfo=None), content=news_item["text"], author=news_item["author"],
                           raw_html=news_item["raw_html"])
        db_session.add(db_item)
        stored_items.append(db_item)
        count += 1

    db_session.commit()
    db_session.close()

    return stored_items

def get_news():
    db_session = db.get_db_session()
    return db_session.query(NewsItem).yield_per(201)
