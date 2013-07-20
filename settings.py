DB_CONNECTION_STRING = "sqlite:///articles.db"

# Dictionary of endpoints; key is a language code, value is URL
SOLR_ENDPOINT_URLS = None #{ "si" : "http://localhost:8984/solr/news/"}
# Default endpoint to dispatch documents in languages without dedicated endpoint
SOLR_DEFAULT_ENDPOINT = "si"
