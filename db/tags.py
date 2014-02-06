from sqlalchemy import Integer, Index, UnicodeText, Column, Table, String, ForeignKey
from sqlalchemy.orm import relationship
import db

news_tags_table = Table('news_tags', db.Base.metadata,
                        Column('news_id', String(128), ForeignKey('news.id')),
                        Column('tag_id', Integer, ForeignKey('tags.id')))

class Tag(db.Base):
    __tablename__ = "tags"
    __table_args__ = (Index('tags_name', 'tag_name'), )

    id = Column(Integer, primary_key=True)
    tag_name = Column(UnicodeText, nullable=False)
    news_items = relationship('NewsItem', secondary=news_tags_table, backref='tags')
