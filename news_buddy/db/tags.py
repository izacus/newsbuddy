from sqlalchemy import Integer, Index, UnicodeText, Column, Table, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import db

news_tags_table = Table('news_tags', db.Base.metadata,
                        Column('news_id', String(128), ForeignKey('news.id', ondelete="CASCADE")),
                        Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE")))

class Tag(db.Base):
    __tablename__ = "tags"
    __table_args__ = (Index('tags_name', 'tag_name'), )

    id = Column(Integer, primary_key=True)
    tag_name = Column(UnicodeText, nullable=False)
    tag_type = Column('tag_type', Enum('PERSON', 'LOCATION', 'OTHER', name="tag_types"), default="OTHER")
    news_items = relationship('NewsItem', secondary=news_tags_table, backref='tags')

    def __repr__(self):
        return unicode(self).encode('ascii', 'replace')

    def __unicode__(self):
        return u"<Tag id=%d name=%s type=%s>" % (self.id, self.tag_name, self.tag_type, )