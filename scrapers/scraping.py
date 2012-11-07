import multiprocessing
import itertools
from rtv_scraper import RTVScraper
from scrapers.delo_scraper import DeloScraper
from scrapers.dnevnik_scraper import DnevnikScraper
from scrapers.zurnal_scraper import ZurnalScraper

def scrape_news():
    scrapers = [RTVScraper(), ZurnalScraper(), DeloScraper(), DnevnikScraper()]
    print "Scraping news!"

    pool = multiprocessing.Pool(processes=4)
    result = pool.map(get_news, scrapers)

    news = [item for sublist in result for item in sublist]
    return news

def get_news(scraper):
    return scraper.get_news()