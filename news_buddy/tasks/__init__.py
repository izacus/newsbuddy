# This establishes Redis connection
from redis import Redis
from rq import Queue
import settings
from tasks import add_article

redis = Redis(host=settings.REDIS_CONFIG["host"], port=settings.REDIS_CONFIG["port"], db=settings.REDIS_CONFIG["db"])


def scrape_news(existing_ids=None):
    from scrapers import scrapers
    queue = Queue('sources', connection=redis)
    for scraper in scrapers:
        queue.enqueue(parse_source, scraper, existing_ids)


def parse_source(scraper, existing_ids):
    articles = scraper.parse_source(existing_ids)
    queue = Queue('articles', connection=redis)
    if articles:
        for article in articles:
            queue.enqueue(parse_article, scraper, article)


def parse_article(scraper, article_url):
    article = scraper.parse_article(article_url)
    if article:
        add_article.add_article(article)
