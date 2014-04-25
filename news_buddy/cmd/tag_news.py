import db
from db.news import NewsItem
from db.tags import Tag
from mining import tagging
from sqlalchemy import func


def tag_news(retag=False):
    db_session = db.get_db_session()

    if retag:
        news_items = db_session.query(NewsItem)
    else:
        # Get newsitems without tags
        news_items = db_session.query(NewsItem).filter(~NewsItem.tags.any())

    tagger = tagging.NewsTagger()

    counter = 0

    write_session = db.get_db_session()
    for news_item in news_items:
        tagger.tag(news_item, db_session=write_session)
        counter += 1
        if counter % 10 == 0:
            print counter
            write_session.commit()

    write_session.commit()

    # Purge all tags without news items
    write_session.query(Tag).filter(~Tag.news_items.any()).delete(synchronize_session='fetch')
    write_session.commit()

    write_session.close()
    db_session.close()