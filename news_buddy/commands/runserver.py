from db.cache import get_cache
import api.v1
from api import app

def runserver(host, port):
    app.run(host, port, debug=True)

    # Clear memcached cache on startup
    cache = get_cache()
    cache.invalidate(True)


@app.route("/")
def root():
    return app.send_static_file("index.html")