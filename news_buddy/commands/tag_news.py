import db
import db.news
from rq import Queue
from db.tags import Tag
from sqlalchemy.orm.exc import NoResultFound
import tasks


def tag_news(retag=False):
    db_session = db.get_db_session()

    # Why is this necessary?!
    try:
        db_session.query(db.tags.Tag).limit(1).one()
    except NoResultFound:
        pass

    if retag:
        news_items = db_session.query(db.news.NewsItem.id)
    else:
        # Get newsitems without tags
        news_items = db_session.query(db.news.NewsItem.id).filter(~db.news.NewsItem.tags.any())

    for item in news_items:
        queue = Queue('ner_tag', connection=tasks.redis)
        queue.enqueue("tasks.tag_article.tag_article", item)
