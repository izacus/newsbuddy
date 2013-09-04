from api import query, stats, related
from cornice import register_service_views


def register(config):
    register_service_views(config, query.news_query)
    register_service_views(config, query.latest)
    register_service_views(config, query.details)
    register_service_views(config, related.related_query)
    register_service_views(config, stats.stats_service)