

def post_to_solr(article):
    import settings
    from pysolarized import solr, to_solr_date
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)

    # Build documents for solr dispatch
    doc = {"id": article["id"], "title": article["title"],
           "source": article["source"], "language": article["language"],
           "source_url": article["source_url"], "content": article["text"],
           "published": to_solr_date(article["published"])}

    if article["author"] is not None:
        doc["author"] = article["author"]

    solr_int.add(doc)
    solr_int._addFlushBatch()