import bs4
import scraping
from scrapers.utils import get_article, get_hash, time_to_datetime, get_sha_hash, get_rss
import logging

logger = logging.getLogger("scraper.zurnal")

class ZurnalScraper(object):

    ZURNAL_RSS_URL = "http://www.zurnal24.si/index.php?ctl=show_rss&url_alias=novice"
    ZURNAL_PRINT_URL = "http://www.zurnal24.si/print/"

    def parse_source(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.ZURNAL_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            news.append((link, {"published": published_date}))

        scraping.parse_articles(self, news)

    def parse_article(self, article_url):
        link, data = article_url
        article_id = link[link.rfind("-") + 1:]
        article = self.get_article_text(article_id)

        published_date = data["published"]
        article["published"] = published_date
        article["source"] = "Zurnal24"
        article["source_url"] = link
        article["language"] = "si"
        # Generate ID from link
        article["id"] = get_sha_hash(link)
        scraping.add_new_article(article)

    def get_article_text(self, article_id):
        logger.debug("Grabbing article ID %s", article_id)
        article_html = get_article(self.ZURNAL_PRINT_URL + str(article_id))
        result = {}
        result["raw_html"] = article_html
        article = bs4.BeautifulSoup(article_html)
        article = article.body.find("article")

        result["title"] = article.hgroup.h1.text
        author = article.find(id="meta_el").find(class_="left").text
        
        try:
            author = author[:author.index('/')].strip() 
            result["author"] = author
        except ValueError as e:
            result["author"] = None 

        content_div = article.find_all("div", class_="entry")
        result["text"] = u" ".join(content_div[0].stripped_strings)
        return result
