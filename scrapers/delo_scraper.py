import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash
import logging

logger = logging.getLogger("scraper.delo")

class DeloScraper(object):
    DELO_RSS_URL = "http://www.delo.si/rss/"

    def get_news(self, existing_ids = None):
        news = []
        feed_content = feedparser.parse(self.DELO_RSS_URL)
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
            article["published"] = published_date
            article["source"] = "Delo"
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
        result["title"] = article.title.text.strip()

        subtitle = article.find(id="EXCERPT", text=True)
        if subtitle is None:
            subtitle = article.find(id="EXCERPT_mnenja", text=True)

        if subtitle is not None:
            result["subtitles"] = [subtitle.text.strip()]

        content_item = article.find(id="D_NEWS")
        if content_item is None:
            content_item = article.find(id="D_NEWS_MNENJA")
        
        author = article.find(class_="d_author")
        if author is not None:
            result["author"] = author.text.strip()
        else:
            result["author"] = None

        if content_item is not None:
            text_content = " ".join([p_item.text.strip() for p_item in content_item.find_all('p', text=True) if p_item is not None])
            result["text"] = text_content
            return result
        else:
            logger.warn("Unknown article content for %s", link)
            return None

