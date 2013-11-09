from multiprocessing.pool import ThreadPool
import itertools
from scrapers.demokracija_scraper import DemokracijaScraper
from scrapers.siol_scraper import SiolScraper
from scrapers.finance_parser import FinanceScraper
from scrapers.mladina_scraper import MladinaScraper
from scrapers.vecer_scraper import VecerScraper
from tfhrs_scraper import TwentyFourHrsScraper
from rtv_scraper import RTVScraper
from scrapers.delo_scraper import DeloScraper
from scrapers.dnevnik_scraper import DnevnikScraper
from scrapers.zurnal_scraper import ZurnalScraper
import logging

logger = logging.getLogger("scraper")

def scrape_news(existing_ids=None):
    scrapers = [DemokracijaScraper(), SiolScraper(), VecerScraper(), FinanceScraper(), MladinaScraper(), TwentyFourHrsScraper(), RTVScraper(), ZurnalScraper(), DeloScraper(), DnevnikScraper()]
    print "Scraping news!"

    pool = ThreadPool(processes=len(scrapers))
    result = pool.map(get_news, itertools.izip(scrapers, itertools.repeat(existing_ids)))

    news = [item for sublist in result for item in sublist]
    return news

def get_news(options):
    scraper, existing_ids = options

    try:
        news = scraper.get_news(existing_ids)    
    except Exception as e:
        logger.error("Failed to parse news from %s", scraper, exc_info=True)

    return news
