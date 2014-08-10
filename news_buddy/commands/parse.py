import logging
import settings
import db.news
import tasks

logger = logging.getLogger("newsbuddy")


def parse_news():
    if settings.SENTRY_CONNECTION_STRING is not None:
        from raven import Client
        from raven.handlers.logging import SentryHandler
        from raven.conf import setup_logging
        logging.basicConfig(level=logging.WARN)
        client = Client(settings.SENTRY_CONNECTION_STRING)
        handler = SentryHandler(client)
        setup_logging(handler)
    else:
        logging.basicConfig(level=logging.DEBUG)

    existing_ids = db.news.get_latest_ids(600)
    tasks.scrape_news(existing_ids)
