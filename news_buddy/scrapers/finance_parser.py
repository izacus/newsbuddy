import logging
import bs4
import scraping
from scrapers.utils import time_to_datetime, get_hash, get_sha_hash, get_article, get_rss

logger = logging.getLogger("scraper.finance")

class FinanceScraper(object):
    FINANCE_RSS_URL = "http://www.finance.si/xml-servis/finance.rss"

    def parse_source(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.FINANCE_RSS_URL)

        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and get_sha_hash(link) in existing_ids:
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            news.append((link, {"published": published_date}))

        scraping.parse_articles(self, news)

    def parse_article(self, article_url):
        link, data = article_url
        article = self.get_article_text(link)

        if article is None: return
        published_date = data["published"]
        article["published"] = published_date
        article["source"] = "Finance"
        article["source_url"] = link
        article["language"] = "si"
        article["id"] = get_sha_hash(link)
        scraping.add_new_article(article)


    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
        article = bs4.BeautifulSoup(article_html)
        if article.body is None:
            return None

        title = article.body.find(class_="article-title")
        result["title"] = title.text.strip()

        author = article.body.find(class_="author")
        if author is not None:
            result["author"] = author.text.strip()
        else:
            result["author"] = None

        subtitle = article.body.find(class_="article-flash")
        if subtitle is not None:
            result["subtitles"] = [subtitle.string.strip()]

        content = article.body.find(class_="art-content")
        if content is None:
            return None
        else:
            result["text"] = u" ".join(content.stripped_strings)
            return result