import logging
import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_sha_hash, get_article

logger = logging.getLogger("scraper.finance")

class FinanceScraper(object):
    FINANCE_RSS_URL = "http://www.finance.si/xml-servis/finance.rss"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = feedparser.parse(self.FINANCE_RSS_URL)

        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and get_sha_hash(link) in existing_ids:
                logger.debug("Skipping %s", link)
                continue

            try:
                article = self.get_article_text(link)
            except Exception as e:
                logger.warn("Failed to parse article %s", link, exc_info=True)
                continue

            if article is None: continue
            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["published"] = published_date
            article["source"] = "Finance"
            article["source_url"] = link
            article["language"] = "si"
            article["id"] = get_sha_hash(link)
            news.append(article)

        return news

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}

        article = bs4.BeautifulSoup(article_html)
        title = article.body.find(class_="article-title")
        result["title"] = title.text.strip()

        author = article.body.find(class_="author")
        if author is not None:
            result["author"] = author.text.strip()
        else:
            result["author"] = None

        subtitle = article.body.find(class_="article-flash")
        if subtitle is not None:
            result["subtitles"] = [subtitle.text.strip()]

        content = article.body.find(class_="art-content")
        if content is None:
            return None
        else:
            result["text"] = content.text.strip()
            return result