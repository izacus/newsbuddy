import logging

import bs4
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss


logger = logging.getLogger("scraper.dnevnik")


class DnevnikScraper(object):
    DNEVNIK_RSS_URL = "http://www.dnevnik.si/rss"

    def parse_source(self, existing_ids = None):
        news = []
        feed_content = get_rss(self.DNEVNIK_RSS_URL)

        max_counter = 30
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            title = feed_entry["title"]
            news.append((link, {"published": published_date, "title": title}))

            max_counter -= 1
            if max_counter <= 0:
                break

        return news

    def parse_article(self, article_url):
        link, data = article_url
        article = self.get_article_text(link)

        if article is None: return
        article["title"] = data["title"]
        article["published"] = data["published"]
        article["source"] = "Dnevnik"
        article["source_url"] = link
        article["language"] = "si"
        article["id"] = get_sha_hash(link)
        return article

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
        article = bs4.BeautifulSoup(article_html)
        
        author = article.body.find(class_="article-source")
        if author is not None and author.strong is not None:
            result["author"] = author.strong.text.strip()
        else:
            result["author"] = None

        subtitle = article.body.find('p', class_="intro-box", text=True)
        if subtitle is not None:
            result["subtitles"] = [subtitle.text.strip()]

        content = article.body.article
        if content is None:
            return None
        else:
            result["text"] = u" ".join(content.stripped_strings)
            return result
