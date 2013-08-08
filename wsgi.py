import api.query
from cornice import register_service_views
from pyramid.config import Configurator

config = Configurator()
config.include('cornice')
register_service_views(config, api.query.news_query)
config.add_static_view('', 'ui')
application = config.make_wsgi_app()
