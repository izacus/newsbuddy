import bs4
import feedparser
from scrapers.utils import get_article, get_hash, time_to_datetime, get_sha_hash
import logging

logger = logging.getLogger("scraper.zurnal")

class ZurnalScraper(object):

    ZURNAL_RSS_URL = "http://www.zurnal24.si/index.php?ctl=show_rss&url_alias=novice"
    ZURNAL_PRINT_URL = "http://www.zurnal24.si/print/"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = feedparser.parse(self.ZURNAL_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            article_id = link[link.rfind("-") + 1:]

            try:
                article = self.get_article_text(article_id)
            except Exception as e:
                logger.warn("Failed to parse article id %s", article_id, exc_info=True)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["published"] = published_date
            article["source"] = "Zurnal24"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            article["id"] = get_sha_hash(link)
            news.append(article)
        return news

    def get_article_text(self, article_id):
        logger.debug("Grabbing article ID %s", article_id)
        article_html = get_article(self.ZURNAL_PRINT_URL + str(article_id))
        result = {}
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
