DB_CONNECTION_STRING = "sqlite:///news.db"

# Dictionary of endpoints; key is a language code, value is URL
SOLR_ENDPOINT_URLS = { "SI" : "http://localhost:8983/solr"}
# Default endpoint to dispatch documents in languages without dedicated endpoint
SOLR_DEFAULT_ENDPOINT = "SI"