
import itertools
import db.news
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
    scrapers = [DeloScraper(), VAL202Scraper(), MonitorScraper()]#, DemokracijaScraper(), SiolScraper(), VecerScraper(), FinanceScraper(), MladinaScraper(), TwentyFourHrsScraper(), RTVScraper(), ZurnalScraper(), DeloScraper(), DnevnikScraper()]

    queue = Queue('sources', connection=get_redis())
    for scraper in scrapers:
        queue.enqueue(scraper.parse_source, existing_ids)

def parse_articles(scraper, article_links):
    queue = Queue('articles', connection=get_redis())
    for article in article_links:
        queue.enqueue(scraper.parse_article, article)

def add_new_article(article):
    db.news.store_news([article])

def get_news(options):
    scraper, existing_ids = options

    try:
        news = scraper.get_news(existing_ids)    
    except Exception as e:
        logger.error("Failed to parse news from %s", scraper, exc_info=True)

    return news
