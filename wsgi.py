import api
import logging
from pyramid.config import Configurator
import settings

config = Configurator()

config.include('cornice')
api.register(config)
config.add_static_view('', 'ui')
application = config.make_wsgi_app()

if settings.SENTRY_CONNECTION_STRING is not None:
    from raven import Client
    from raven.middleware import Sentry

    client = Client(settings.SENTRY_CONNECTION_STRING)
    application = Sentry(application, client=client)
    client.logger.setLevel(logging.WARNING)
