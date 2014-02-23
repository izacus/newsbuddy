from db.cache import FromCache
from lemmagen import lemmatizer
import db
from sqlalchemy.orm.exc import NoResultFound
from mining.entity_extractor import EntityExtractor
from db.tags import Tag     # Must be imported for NewsItem reverse mapping


class NewsTagger:

    def __init__(self):
        self.tagger = EntityExtractor()
        self.lemmatizer = lemmatizer.Lemmatizer()

    def tag(self, news_item, db_session=None):
        tags = []

        news_item_tags = self.tagger.tag(" ".join([news_item.title, news_item.content]))
        if news_item_tags is None:
            return tags

        if db_session:
            s = db_session
        else:
            s = db.get_db_session()

        news_item.tags = []
        s.add(news_item)

        for news_tag, news_tag_type in news_item_tags:
            news_tag = self.lemmatizer.lemmatize(news_tag).strip()
            try:
                tag = s.query(db.tags.Tag).filter_by(tag_name=news_tag).options(FromCache("tags")).one()
            except NoResultFound:
                tag = db.tags.Tag(tag_name=news_tag, tag_type=news_tag_type)

            tag.news_items.append(news_item)
            s.add(tag)
            tags.append(tag)

        if not db_session:
            s.commit()

        return tags