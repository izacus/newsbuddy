import scrapers
from solr import solr

news = scrapers.scrape_news()

solr_int = solr.SolrInterface({ "SI" : "http://localhost:8983/solr/"}, "SI")
solr_int.deleteAll()

# Build documents for solr dispatch
docs = []
for news_item in news:
    print u"Dispatching ", news_item["title"]
    doc = { "id" : news_item["id"], "title" : news_item["title"], \
            "source" : news_item["source"], "language" : news_item["language"], \
            "source_url" : news_item["source_url"], "content" : news_item["text"], \
            "published" : solr.to_solr_date(news_item["published"]) } 
    docs.append(doc)

solr_int.add(docs)
solr_int.commit()


    
