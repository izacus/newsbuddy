import db
from db.news import NewsItem
from db.tags import Tag
from mining import tagging


def tag_news(retag=False):
    db_session = db.get_db_session()

    if retag:
        news_items = db_session.query(NewsItem).all()
    else:
        # Get newsitems without tags
        news_items = db_session.query(NewsItem).filter(~NewsItem.tags.any()).all()

    tagger = tagging.NewsTagger()

    counter = 0
    for news_item in news_items:
        tagger.tag(news_item, db_session=db_session)
        counter += 1
        if counter % 10 == 0:
            print counter, "/", len(news_items)
            db_session.commit()

    db_session.commit()

    # Purge all tags without news items
    db_session.query(Tag).filter(~Tag.news_items.any()).delete(synchronize_session='fetch')
    db_session.commit()

    db_session.close()