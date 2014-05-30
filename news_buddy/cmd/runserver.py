#from db.cache import get_cache
from news_buddy import app
import news_buddy.api.v1

def runserver(host, port):
    app.run(host, port, debug=True)

    # logging.basicConfig(level=logging.DEBUG)
    # config = Configurator()
    # config.include('cornice')
    # api.register(config)
    # config.add_static_view('', '../../ui')
    # config.add_renderer('atom', AtomRenderer)
    # app = config.make_wsgi_app()
    # server = make_server(host, port, app)
    # server.serve_forever()

    # Clear memcached cache on startup
    #cache = get_cache()
    #cache.invalidate(True)


@app.route("/")
def root():
    return app.send_static_file("index.html")