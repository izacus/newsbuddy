import api
import logging
from pyramid.config import Configurator
import settings

config = Configurator(settings={
    'cache.type': 'ext:memcached',
    'cache.regions': 'news',
    'cache.news.expires': '7200',
    'cache.url': '127.0.0.1:11211'
})

config.include('cornice')
config.include('pyramid_beaker')
api.register(config)
config.add_static_view('', 'ui')
application = config.make_wsgi_app()

if settings.SENTRY_CONNECTION_STRING is not None:
    from raven import Client
    from raven.middleware import Sentry

    client = Client(settings.SENTRY_CONNECTION_STRING)
    application = Sentry(application, client=client)
    client.logger.setLevel(logging.WARNING)
