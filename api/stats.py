import logging
from datetime import datetime
from cornice import Service
import db
from db.news import NewsItem
from sqlalchemy import func

logger = logging.getLogger("api.stats")

stats_service = Service(name="news_stats", path="/news/stats/", description="Returns news statistics")
stats = None

@stats_service.get()
def get_stats(request):
    global stats
    if stats is None:
        try:
            db_session = db.news.get_db_session()
            stats = {}
            num_news = db_session.query(func.count(NewsItem.id)).scalar()
            stats["total_news"] = num_news

            # News by source
            news_by_source = db_session.query(NewsItem.source, func.count(NewsItem.id)).group_by(NewsItem.source).all()
            stats["total_by_source"] = {}
            for item in news_by_source:
                stats["total_by_source"][item[0]] = item[1]

            midnight_today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            news_today = db_session.query(func.count(NewsItem.id)).filter(NewsItem.published > midnight_today).scalar()
            stats["news_today"] = news_today

        except Exception as e:
            logger.error("Failed to get stats.", exc_info=True)
            raise

    return stats

@stats_service.delete()
def delete_stats(request):
    global stats
    stats = None
    return None