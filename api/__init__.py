from api import query, stats
from cornice import register_service_views


def register(config):
    register_service_views(config, query.news_query)
    register_service_views(config, stats.stats_service)