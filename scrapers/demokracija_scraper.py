from lxml import etree
import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss
import logging

logger = logging.getLogger("scraper.demokracija")


class DemokracijaScraper(object):
    """
    Scraper contributed by Gasper Setinc
    """
    DEMOKRACIJA_RSS_URL = "http://demokracija.si/index.php?format=feed&type=rss"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.DEMOKRACIJA_RSS_URL)

        max_counter = 30
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            try:
                article = self.get_article_text(link)
            except Exception as e:
                logger.warn("Failed to parse article %s", link, exc_info=True)
                continue

            if article is None: continue
            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["title"] = feed_entry["title"]
            article["author"] = feed_entry["author"] if "author" in feed_entry else None
            article["published"] = published_date
            article["source"] = "Demokracija"
            article["source_url"] = link
            article["language"] = "si"
            article["id"] = get_sha_hash(link)
            news.append(article)

            max_counter -= 1
            if max_counter <= 0:
                break
        return news

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
        tree = etree.fromstring(article_html, etree.HTMLParser())
        result["text"] = '\n'.join(tree.xpath('//div[@class="article"]/p[string-length(@class) = 0]//text()'))
        result["subtitles"] = [text.strip() for text in tree.xpath('//div[@class="article"]/p/strong/text()')]
        return result

