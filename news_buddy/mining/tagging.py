import logging
from lemmagen import lemmatizer
import db
import db.news
from sqlalchemy.orm.exc import NoResultFound
from mining.entity_extractor import EntityExtractor
from db.tags import Tag     # Must be imported for NewsItem reverse mapping
from db.cache import FromCache

logger = logging.getLogger("mining.newstagger")

class NewsTagger:
    db_session = None

    def __init__(self):
        self.tagger = EntityExtractor()
        self.lemmatizer = lemmatizer.Lemmatizer()

    def tag(self, news_item_id):
        if not self.db_session:
            self.db_session = db.get_db_session()

        s = self.db_session
        news_item = s.query(db.news.NewsItem).filter_by(id=news_item_id).one()
        s.add(news_item)
        news_item_tags = self.tagger.tag(" ".join([news_item.title, news_item.content]))
        if news_item_tags is None:
            return

        news_item.tags = []
        for tag in news_item_tags:
            news_tag = self.lemmatizer.lemmatize(tag[0]).strip()
            try:
                tag = s.query(db.tags.Tag).filter_by(tag_name=tag[0]).options(FromCache("tags")).one()
            except NoResultFound:
                tag = db.tags.Tag(tag_name=news_tag, tag_type=tag[1])

            tag.news_items.append(news_item)
            s.add(tag)

        s.commit()
        logger.info("Tagged %s." % (news_item, ))

# Cache tagger instance
tagger = NewsTagger()