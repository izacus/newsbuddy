import logging
import bs4
import scraping
from scrapers.utils import get_hash, time_to_datetime, get_article, get_sha_hash, get_rss

logger = logging.getLogger("scraper.mladina")

class MladinaScraper(object):

    MLADINA_RSS = "http://feeds.feedburner.com/Mladina"

    def parse_source(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.MLADINA_RSS)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
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
        article["source"] = "Mladina"
        article["source_url"] = link
        article["language"] = "si"
        # Generate ID from link
        article["id"] = get_sha_hash(link)
        scraping.add_new_article(article)

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)

        result = {}
        article_html = get_article(link)
        result["raw_html"] = article_html
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