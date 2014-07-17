from lxml import etree
import bs4
import feedparser
import scraping
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss
import logging

logger = logging.getLogger("scraper.demokracija")


class DemokracijaScraper(object):
    """
    Scraper contributed by Gasper Setinc
    """
    DEMOKRACIJA_RSS_URL = "http://demokracija.si/index.php?format=feed&type=rss"

    def parse_source(self, existing_ids = None):
        news = []
        feed_content = get_rss(self.DEMOKRACIJA_RSS_URL)

        max_counter = 30
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            title = feed_entry["title"]
            author = feed_entry["author"] if "author" in feed_entry else None
            news.append((link, { "title": title, "author": author, "published": published_date}))

            max_counter -= 1
            if max_counter <= 0:
                break

        scraping.parse_articles(self, news)

    def parse_article(self, article_url):
        link, data = article_url

        article = self.get_article_text(link)
        if article is None:
            return

        article["title"] = data["title"]
        article["author"] = data["author"]
        article["published"] = data["published"]
        article["source"] = "Demokracija"
        article["source_url"] = link
        article["language"] = "si"
        article["id"] = get_sha_hash(link)

        scraping.add_new_article(article)

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
        tree = etree.fromstring(article_html, etree.HTMLParser())
        result["text"] = '\n'.join(tree.xpath('//div[@class="article"]/p[string-length(@class) = 0]//text()'))
        result["subtitles"] = [text.strip() for text in tree.xpath('//div[@class="article"]/p/strong/text()')]
        return result

