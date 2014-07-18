# -*- coding: utf-8 -*-
import logging
import lxml.html
import re
from lxml import etree
import scraping
import nltk
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss

logger = logging.getLogger("scraper.24ur")

class TwentyFourHrsScraper(object):

    TFH_RSS_URL = "http://www.24ur.com/rss/"

    def parse_source(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.TFH_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            title = feed_entry["title"]

            news.append((link, {"published": published_date, "title": title}))

        scraping.parse_articles(self, news)

    def parse_article(self, article_url):
        link, data = article_url

        article = self.get_article(link)
        if article is None: return

        published_date = data["published"]
        article["title"] = data["title"]
        article["published"] = published_date
        article["source"] = "24ur"
        article["source_url"] = link
        article["language"] = "si"
        # Generate ID from link
        article["id"] = get_sha_hash(link)
        scraping.add_new_article(article)

    def get_article(self, link):
        logger.debug("Grabbing article %s", link)

        article_html = get_article(link.replace("24ur.com", "www.24ur.com"))
        result = {}
        result["raw_html"] = article_html
        tree = etree.fromstring(article_html, etree.HTMLParser())
        summary = tree.xpath('//div[@class="summary"]/p/text()')
        result["subtitles"] = unicode(summary)

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
