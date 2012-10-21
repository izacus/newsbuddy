from rtv_scraper import RTVScraper

def scrape_news():
    print "Scraping news!"
    rtv_scraper = RTVScraper()
    news = rtv_scraper.get_news()
    return news
