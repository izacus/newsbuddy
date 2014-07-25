import logging
from db.cache import FromCache
from lemmagen import lemmatizer
import db
import db.news
from mining.entity_extractor import EntityExtractor
from sqlalchemy.orm.exc import NoResultFound
from db.tags import Tag     # Must be imported for NewsItem reverse mapping

logger = logging.getLogger("mining.newstagger")

tagger = EntityExtractor()
lem = lemmatizer.Lemmatizer()


def tag_article(article_id):
    logger.info("Tagging %s..." % str(article_id))

    s = db.get_db_session()
    article = s.query(db.news.NewsItem).filter_by(id=article_id).one()
    s.add(article)

    article_tags = tagger.tag(" ".join([article.title, article.content]))
    if article_tags is None:
        return

    article.tags = []
    for tag in article_tags:
        news_tag = lem.lemmatize(tag[0]).strip()
        try:
            tag = s.query(db.tags.Tag).filter_by(tag_name=news_tag).options(FromCache("tags")).one()
        except NoResultFound:
            tag = db.tags.Tag(tag_name=news_tag, tag_type=tag[1])
        tag.news_items.append(article)
        s.add(tag)

    s.commit()
    logger.info("Found %d tags." % len(article.tags))