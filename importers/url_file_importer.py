import sys
from scrapers.dnevnik_scraper import DnevnikScraper


def import_dnevnik():
    url_file = open(sys.argv[2], "rb")
    scraper = DnevnikScraper()
    for line in url_file:
        url = line.strip()
        article = scraper.get_article_text(url)
        print article

if sys.argv[1] == "dnevnik":
    import_dnevnik()