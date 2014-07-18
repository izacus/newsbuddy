import logging
from mining import tagging
import requests
import scrapers
import settings
import db.news
from pysolarized import to_solr_date
from pysolarized import solr

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

    try:
        existing_ids = db.news.get_latest_ids(800)
        scrapers.scrape_news(existing_ids)
    except Exception as e:
        logger.error("Failed to process work packet!", exc_info=True)
