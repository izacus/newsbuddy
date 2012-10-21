from wsgiref.simple_server import make_server
import api.query
from cornice import register_service_views
from pyramid.config import Configurator

if __name__ == "__main__":
    config = Configurator()
    config.include('cornice')
    register_service_views(config, api.query.news_query)

    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8000, app)
    server.serve_forever()

