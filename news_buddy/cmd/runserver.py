import logging
from wsgiref.simple_server import make_server
import api
from api.v1.query import AtomRenderer
from pyramid.config import Configurator
from db.cache import get_cache

def runserver(host, port):
    logging.basicConfig(level=logging.DEBUG)
    config = Configurator()
    config.include('cornice')
    api.register(config)
    config.add_static_view('', '../ui')
    config.add_renderer('atom', AtomRenderer)
    app = config.make_wsgi_app()
    server = make_server(host, port, app)
    server.serve_forever()

    # Clear memcached cache on startup
    cache = get_cache()
    cache.invalidate(True)
