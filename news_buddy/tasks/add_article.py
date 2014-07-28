
def add_article(article):
    from rq import Queue
    import tasks

    import db.news
    db.news.store_news([article])
    queue = Queue('solr_dispatch', connection=tasks.redis)
    queue.enqueue("tasks.post_to_solr.post_to_solr", article)
    queue = Queue('ner_tag', connection=tasks.redis)
    queue.enqueue("tasks.tag_article.tag_article", article["id"])
