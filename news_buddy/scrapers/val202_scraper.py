import logging
import bs4
from lxml import etree
from scrapers.utils import get_rss, get_sha_hash, time_to_datetime, get_article

logger = logging.getLogger("scraper.val202")

class VAL202Scraper(object):

    VAL202_RSS_URL = "http://www.val202.si/feed/"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.VAL202_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            guid = feed_entry["guid"]
            if existing_ids and get_sha_hash(guid) in existing_ids:
                logger.debug("Skipping %s", guid)
                continue

            article = {}
            try:
                article_html = get_article(link)
                article["raw_html"] = article_html
            except Exception as e:
                logger.warn("Failed to parse article %s", link, exc_info=True)
                continue

            try:
                text = feed_entry["content"][0]["value"]
                # Strip HTML
                soup = bs4.BeautifulSoup(text)
                article["text"] = soup.text
            except KeyError:
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["title"] = feed_entry["title"]
            article["published"] = published_date
            article["source"] = "Val202"
            article["source_url"] = link
            article["language"] = "si"
            article["author"] = None
            if "author" in feed_entry:
                article["author"] = feed_entry["author"]

            # Generate ID from link
            article["id"] = get_sha_hash(guid)
            news.append(article)
        return news