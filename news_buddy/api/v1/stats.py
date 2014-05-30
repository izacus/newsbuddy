import logging
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from news_buddy import app

import db
from db.cache import get_cache
from db.news import NewsItem

logger = logging.getLogger("api.stats")
cache = get_cache()


@app.route("/v1/news/stats/", methods=["GET"])
def get_stats():
    return build_stats()


@cache.cache_on_arguments()
def build_stats():
    db_session = db.get_db_session()
    try:
        stats = {}
        num_news = db_session.query(func.count(NewsItem.id)).scalar()
        stats["total_news"] = num_news

        # News by source
        news_by_source = db_session.query(NewsItem.source, func.count(NewsItem.id)).group_by(NewsItem.source).all()
        stats["total_by_source"] = {}
        for item in news_by_source:
            stats["total_by_source"][item[0]] = item[1]

        midnight_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        news_by_source_today = db_session.query(NewsItem.source, func.count(NewsItem.id)).filter(NewsItem.published > midnight_today).group_by(NewsItem.source).all()
        stats["total_by_source_today"] = {}
        for item in news_by_source_today:
            stats["total_by_source_today"][item[0]] = item[1]

        news_today = db_session.query(func.count(NewsItem.id)).filter(NewsItem.published > midnight_today).scalar()
        stats["news_today"] = news_today

        # Get stats for last month
        this_month = datetime.utcnow() - timedelta(30)
        years = extract('year', NewsItem.published).label("years")
        months = extract('month', NewsItem.published).label('months')
        days = extract('day', NewsItem.published).label('days')
        news_by_day = db_session.query(years, months, days, func.count(NewsItem.id)) \
                                .filter(NewsItem.published > this_month) \
                                .group_by(years, months, days)\
                                .order_by(years, months, days)

        stats["news_by_day"] = {}
        for years, month, day, count in news_by_day:
            stats["news_by_day"]["%04d-%02d-%02d" % (years, month, day)] = count

    except Exception as e:
        logger.error("Failed to get stats.", exc_info=True)
        db_session.rollback()
        raise
    finally:
        db_session.close()

    return stats


@app.route("/v1/news/stats/", methods=["DELETE"])
def delete_stats():
    cache.invalidate(True)
    # Re-heat cache
    build_stats()
    import news_buddy.api.v1.query
    news_buddy.api.v1.query.build_latest_news(0)