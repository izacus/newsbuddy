import logging
from db.cache import FromCache
from lemmagen import lemmatizer
import db
import db.news
from mining.entity_extractor import EntityExtractor
from sqlalchemy.orm import load_only, Load, defer
from sqlalchemy.orm.exc import NoResultFound
from db.tags import Tag     # Must be imported for NewsItem reverse mapping

logger = logging.getLogger("mining.newstagger")

tagger = EntityExtractor()
lem = lemmatizer.Lemmatizer()


def tag_article(article_id):
    logger.info("Tagging %s..." % str(article_id))

    s = db.get_db_session()
    try:
        _tag_article_inner(s, article_id)
        s.commit()
    except:
        s.rollback()
        raise


def _tag_article_inner(s, article_id):
    article = s.query(db.news.NewsItem).options(load_only('id', 'title', 'content')).get(article_id)
    s.add(article)

    article_tags = tagger.tag(" ".join([article.title, article.content]))
    if article_tags is None:
        s.close()
        return

    article.tags = []

    # Counter is here to curb memory usage
    for tag_name, tag_type in article_tags:
        news_tag = lem.lemmatize(tag_name).strip()
        try:
            tag = s.query(db.tags.Tag).filter_by(tag_name=news_tag).options(FromCache("tags")).one()
        except NoResultFound:
            tag = db.tags.Tag(tag_name=news_tag, tag_type=tag_type)
        article.tags.append(tag)
