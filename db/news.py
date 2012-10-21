from sqlalchemy import Column, String, UnicodeText, DateTime, Unicode
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewsItem(Base):
    __tablename__ = "news"

    id = Column(String, primary_key=True)
    title = Column(UnicodeText)
    published = Column(DateTime)
    source = Column(Unicode)
    source_url = Column(Unicode)
    content = Column(UnicodeText)

def create_news_db(engine):
    Base.metadata.create_all(engine)