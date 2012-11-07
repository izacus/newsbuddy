from rtv_scraper import RTVScraper
from scrapers.delo_scraper import DeloScraper
from scrapers.zurnal_scraper import ZurnalScraper

def scrape_news():
    print "Scraping news!"
    news = []
    rtv_scraper = RTVScraper()
    news.extend(rtv_scraper.get_news())
    zurnal_scraper = ZurnalScraper()
    news.extend(zurnal_scraper.get_news())
    delo_scraper = DeloScraper()
    news.extend(delo_scraper.get_news())
    return news
