
import itertools
import db.news
from mining import tagging
from pysolarized import solr, to_solr_date
from redis import Redis
from rq import Queue
from scrapers.demokracija_scraper import DemokracijaScraper
from scrapers.monitor_scraper import MonitorScraper
from scrapers.siol_scraper import SiolScraper
from scrapers.finance_parser import FinanceScraper
from scrapers.mladina_scraper import MladinaScraper
from scrapers.val202_scraper import VAL202Scraper
from scrapers.vecer_scraper import VecerScraper
import settings
from tfhrs_scraper import TwentyFourHrsScraper
from rtv_scraper import RTVScraper
from scrapers.delo_scraper import DeloScraper
from scrapers.dnevnik_scraper import DnevnikScraper
from scrapers.zurnal_scraper import ZurnalScraper
import logging

logger = logging.getLogger("scraper")

redis = None

def get_redis():
    global redis
    if not redis:
        redis = Redis(host=settings.REDIS_CONFIG["host"], port=settings.REDIS_CONFIG["port"], db=settings.REDIS_CONFIG["db"])
    return redis

def scrape_news(existing_ids=None):
    scrapers = [DeloScraper(), VAL202Scraper(), MonitorScraper(), DemokracijaScraper(), SiolScraper(), VecerScraper(), FinanceScraper(), MladinaScraper(), TwentyFourHrsScraper(), RTVScraper(), ZurnalScraper(), DeloScraper(), DnevnikScraper()]

    queue = Queue('sources', connection=get_redis())
    for scraper in scrapers:
        queue.enqueue(scraper.parse_source, existing_ids)

def parse_articles(scraper, article_links):
    queue = Queue('articles', connection=get_redis())
    for article in article_links:
        queue.enqueue(scraper.parse_article, article)

def add_new_article(article):
    db.news.store_news([article])
    queue = Queue('articles_dispatch', connection=get_redis())
    queue.enqueue(tag_new_article, article["id"])
    queue.enqueue(dispatch_to_solr, [article])

def tag_new_article(article_id):
    news_tagger = tagging.NewsTagger()
    news_tagger.tag(article_id)

def dispatch_to_solr(news):
    solr_int = solr.Solr(settings.SOLR_ENDPOINT_URLS, settings.SOLR_DEFAULT_ENDPOINT)
    # Build documents for solr dispatch
    docs = []
    for news_item in news:
        doc = { "id" : news_item["id"], "title" : news_item["title"],
                "source" : news_item["source"], "language" : news_item["language"],
                "source_url" : news_item["source_url"], "content" : news_item["text"],
                "published" : to_solr_date(news_item["published"]) }

        if news_item["author"] is not None:
            doc["author"] = news_item["author"]

        docs.append(doc)

    solr_int.add(docs)
    solr_int.commit()



def get_news(options):
    scraper, existing_ids = options

    try:
        news = scraper.get_news(existing_ids)    
    except Exception as e:
        logger.error("Failed to parse news from %s", scraper, exc_info=True)

    return news
