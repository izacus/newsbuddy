# -*- coding: utf-8 -*-
import logging
import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash

logger = logging.getLogger("scraper.24ur")

class TwentyFourHrsScraper(object):

    TFH_RSS_URL = "http://www.24ur.com/rss/"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = feedparser.parse(self.TFH_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            try:
                article = self.get_article(link)
            except Exception as e:
                logger.warn("Failed to parse article %s", link, exc_info=True)
                continue

            if article is None:
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["title"] = feed_entry["title"]
            article["published"] = published_date
            article["source"] = "24ur"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            article["id"] = get_sha_hash(link)
            news.append(article)
        return news

    def get_article(self, link):
        logger.debug("Grabbing article %s", link)

        article_html = get_article(link.replace("24ur.com", "www.24ur.com"))
        result = {}

        article = bs4.BeautifulSoup(article_html)

        summary = article.find(class_="summary")
        if summary is not None:
            result["subtitles"] = summary.text.strip()

        # Try to find author
        author_container = article.find(class_="containerLeftSide")
        if author_container is not None:
            container_text = author_container.text.strip()
            author = container_text[container_text.rfind('|'):]
            result["author"] = author
        else:
            result["author"] = None

        text = article.find(id="content")
        result["text"] = text.text.strip()
        if u"Preverite vpisani naslov ali uporabite možnost iskanja po naših straneh." in result["text"]:
            return None
        return result
