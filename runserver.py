import logging
from wsgiref.simple_server import make_server
import api
from api.v1.query import AtomRenderer
from pyramid.config import Configurator

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    config = Configurator()
    config.include('cornice')
    api.register(config)
    config.add_static_view('', 'ui')
    config.add_renderer('atom', AtomRenderer)
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8005, app)
    server.serve_forever()
