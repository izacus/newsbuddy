from cornice import register_service_views
from api.v1 import query, related, stats


def register(config):
    register_service_views(config, query.news_query)
    register_service_views(config, query.latest)
    register_service_views(config, query.details)
    register_service_views(config, related.related_query)
    register_service_views(config, stats.stats_service)
    register_service_views(config, query.query_suggest)