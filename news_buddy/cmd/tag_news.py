import db
from db.news import NewsItem
from rq import Queue
import tasks


def tag_news(retag=False):
    db_session = db.get_db_session()

    if retag:

        news_items = db_session.query(NewsItem.id)
    else:
        # Get newsitems without tags
        news_items = db_session.query(NewsItem.id).filter(~NewsItem.tags.any())

    for item in news_items:
        queue = Queue('articles_dispatch', connection=tasks.redis)
        queue.enqueue("tasks.tag_article.tag_article", item)
