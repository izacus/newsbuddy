import api.query
from cornice import register_service_views
from pyramid.config import Configurator
import settings

config = Configurator()
config.include('cornice')
register_service_views(config, api.query.news_query)
config.add_static_view('', 'ui')
application = config.make_wsgi_app()

if settings.SENTRY_CONNECTION_STRING is not None:
   from raven import Client
   from raven.middleware import Sentry
   client = Client(settings.SENTRY_CONNECTION_STRING)
   application = Sentry(application, client=client)
