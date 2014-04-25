from sqlalchemy import func
import db
from db.news import NewsItem


def purge_duplicates(do_commit):
    s = db.get_db_session()

    doubled_urls = s.query(NewsItem.source_url, func.count(NewsItem.source_url))\
                    .group_by(NewsItem.source_url)\
                    .having(func.count(NewsItem.source_url) > 1)

    counter = 0
    for url, count in doubled_urls:
        news_items = s.query(NewsItem).filter_by(source_url=url).order_by(-func.length(NewsItem.id)).all()
        for item in news_items[1:]:
            counter += 1
            print "Should delete", item.id

            if do_commit:
                s.delete(item)

    print "Commiting deletion for total of", counter, "items."
    s.commit()
