DB_CONNECTION_STRING = "sqlite:///articles.db"
LOCAL_URL = "http://localhost:8005"
SENTRY_CONNECTION_STRING = None
# Dictionary of endpoints; key is a language code, value is URL
SOLR_ENDPOINT_URLS = { "si" : "http://localhost:8983/solr/news/"}
# Default endpoint to dispatch documents in languages without dedicated endpoint
SOLR_DEFAULT_ENDPOINT = "si"
# Url of memcached server for caching
REDIS_CONFIG = { "host": None, "port": None, "db": None }
# Url of NER service
NER_SERVICE_URL = None