import api
from api.v1.query import AtomRenderer
import logging
from pyramid.config import Configurator
from db.cache import get_cache
import settings

config = Configurator()

config.include('cornice')
api.register(config)
config.add_static_view('', 'ui')
config.add_renderer('atom', AtomRenderer)
application = config.make_wsgi_app()

# Clear memcached cache on startup
cache = get_cache()
cache.invalidate(True)

if settings.SENTRY_CONNECTION_STRING is not None:
    from raven import Client
    from raven.middleware import Sentry

    client = Client(settings.SENTRY_CONNECTION_STRING)
    application = Sentry(application, client=client)
    client.logger.setLevel(logging.WARNING)
