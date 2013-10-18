import logging
from lxml import etree
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_sha_hash, get_article

logger = logging.getLogger("scraper.finance")

class SiolScraper(object):
    """
    Scraper contributed by Gasper Setinc
    """
    SIOL_RSS_URL = "http://www.siol.net/rss.aspx?path=SiOL.Net"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = feedparser.parse(self.SIOL_RSS_URL)

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
            article["title"] = feed_entry["title"]
            article["source"] = "Siol.net"
            article["source_url"] = link
            article["language"] = "si"
            article["id"] = get_sha_hash(link)
            print article
            news.append(article)

        return news

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}

        tree = etree.fromstring(article_html, etree.HTMLParser())

        # This is a structure for editorials
        author = None

        try:
            author = tree.xpath('//article[@id="article"]/div')[1].xpath("./text()")[2].strip()
        except:
            try:
                a = tree.xpath('//article[@id="article"]/header/p')[0].xpath('./i/text()')[0].strip()
                if "Avtor:" in a:
                    author = a.replace("Avtor:", "").strip()
            except:
                author = None

        result["author"] = author
        result["subtitles"] = [' '.join(tree.xpath('//article[@id="article"]/header')[0].xpath('./p')[-1].xpath('./text()')).strip()]
        result["text"] = '\n\n'.join([' '.join(x).strip() for x in map(lambda x: x.xpath('.//text()'), tree.xpath('//article[@id="article"]/p'))]).strip()

        return result