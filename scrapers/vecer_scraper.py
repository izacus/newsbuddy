import logging
import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss

logger = logging.getLogger("scraper.vecer")

class VecerScraper(object):

    VECER_RSS_URL = "http://mix.vecer.com/rss/"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.VECER_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and get_sha_hash(link) in existing_ids:
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
            article["source"] = "Vecer"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            article["id"] = get_sha_hash(link)
            news.append(article)
        return news

    def get_article(self, link):
        logger.debug("Grabbing article %s", link)

        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
        article = bs4.BeautifulSoup(article_html)

        # Try to find the subtitle
        subtitle = article.find('font', size=3, color="#ff8000")
        if subtitle is not None and subtitle.find('b') is not None:
            result["subtitles"] = [subtitle.b.text.strip()]

        author = article.find('div', class_="clanekAVTOR")
        if author is not None:
            result["author"] = author.text.strip()
        else:
            result["author"] = None

        text_container = article.find(id="_xclaimwords_wrapper")
        if text_container is None:
            return None

        # Remove all script tags from text container
        scripts = text_container.findAll('script')
        [script.extract() for script in scripts]
        result["text"] = u" ".join(text_container.stripped_strings)
        return result