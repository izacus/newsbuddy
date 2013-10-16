import logging
from wsgiref.simple_server import make_server
import api
from pyramid.config import Configurator

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = Configurator(settings={
        'cache.regions': 'news',
        'cache.type': 'memory',
        'cache.news.expires': '7200'
    })
    config.include('cornice')
    config.include('pyramid_beaker')
    api.register(config)
    config.add_static_view('', 'ui')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8005, app)
    server.serve_forever()