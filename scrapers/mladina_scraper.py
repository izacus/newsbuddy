import logging
import bs4
import feedparser
from scrapers.utils import get_hash, time_to_datetime, get_article, get_sha_hash

logger = logging.getLogger("scraper.mladina")

class MladinaScraper(object):

    MLADINA_RSS = "http://feeds.feedburner.com/Mladina"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = feedparser.parse(self.MLADINA_RSS)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                logger.debug("Skipping %s", link)
                continue

            try:
                article = self.get_article_text(link)
            except Exception as e:
                logger.warn("Failed to parse article %s!", link, exc_info=True)
                continue

            if article is None: continue
            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["published"] = published_date
            article["source"] = "Mladina"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            article["id"] = get_sha_hash(link)
            news.append(article)

        return news

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)

        result = {}
        article_html = get_article(link)
        article = bs4.BeautifulSoup(article_html)

        main_part = article.find(class_="main")
        title = main_part.find('h1')

        if title is None:
            return None

        result["title"] = title.text.strip()

        subtitles = main_part.findAll('h2')
        result["subtitles"] = []
        for subtitle in subtitles:
            result["subtitles"].append(subtitle.text.strip())

        # Find author
        info_part = main_part.find('p', class_="info")
        try:
            author = info_part.text[:info_part.text.find('|')].strip()
            result["author"] = author
        except ValueError:
            result["author"] = None

        # Content
        content_items = main_part.findAll(attrs={'class': None})
        content = u"\n".join([u"\n".join(item.stripped_strings) for item in content_items])
        result["text"] = content
        return result