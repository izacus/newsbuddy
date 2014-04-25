# -*- coding: utf-8 -*-
import logging
import lxml.html
import re
from lxml import etree
import feedparser
import nltk
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss

logger = logging.getLogger("scraper.24ur")

class TwentyFourHrsScraper(object):

    TFH_RSS_URL = "http://www.24ur.com/rss/"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.TFH_RSS_URL)
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
        result["raw_html"] = article_html
        tree = etree.fromstring(article_html, etree.HTMLParser())
        summary = tree.xpath('//div[@class="summary"]/p/text()')
        result["subtitles"] = summary

        author_texts = tree.xpath("//div[@class='containerLeftSide']/text()")
        author_text = u" ".join(text.strip() for text in author_texts)
        if u"|" in author_text:
            author = author_text[author_text.rfind('|'):]
        else:
            author = None

        result["author"] = author

        # Elaborate way of getting rid of all script tags and other garbage in this HTML. Looking for
        # a better way.
        content = tree.xpath("//div[@id='content']")
        if len(content) == 0:
            return None

        text = re.sub("\s\s+", " ", nltk.clean_html(lxml.html.tostring(content[0], encoding="utf-8").decode("utf-8")))
        result["text"] = text
        if u"Preverite vpisani naslov ali uporabite možnost iskanja po naših straneh." in result["text"]:
            return None
        return result
