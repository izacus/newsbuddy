from news_buddy import app
import logging
from db.cache import get_cache
import settings

application = app

# Clear memcached cache on startup
cache = get_cache()
cache.invalidate(True)

if settings.SENTRY_CONNECTION_STRING is not None:
    from raven import Client
    from raven.middleware import Sentry

    client = Client(settings.SENTRY_CONNECTION_STRING)
    application = Sentry(application, client=client)
    client.logger.setLevel(logging.WARNING)
