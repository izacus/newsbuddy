from sqlalchemy import Integer, String, Index, ForeignKey, UnicodeText
from sqlalchemy.orm import relationship
from sqlalchemy.testing.schema import Column, Table
import db

news_tag_table = Table('news_tags', db.Base.metadata,
                       Column('tag_id', Integer, ForeignKey('tags.id')),
                       Column('news_id', String, ForeignKey('news.id')))

class Tag(db.Base):
    __tablename__ = "tags"
    __table_args__ = (Index('tags_name', 'tag_name'))

    id = Column(Integer, primary_key=True)
    tag_name = Column(UnicodeText, nullable=False)
    news_items = relationship('NewsItem', secondary=news_tag_table)