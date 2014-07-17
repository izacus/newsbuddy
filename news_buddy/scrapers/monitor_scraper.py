import logging
from lxml import etree
import scraping
from scrapers.utils import get_rss, get_sha_hash, time_to_datetime, get_article

logger = logging.getLogger("scraper.monitor")

class MonitorScraper(object):

    MONITOR_RSS_URL = "http://www.monitor.si/media/rss/rss-fb-monitor-novice.xml"

    def parse_source(self, existing_ids = None):
        article_urls = []
        feed_content = get_rss(self.MONITOR_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            guid = feed_entry["guid"]

            if existing_ids and get_sha_hash(guid) in existing_ids:
                logger.debug("Skipping %s", guid)
                return

            published_date = time_to_datetime(feed_entry["published_parsed"])
            title = feed_entry["title"]

            article_urls.append((link, {"guid": guid, "title": title, "published": published_date}))
        scraping.parse_articles(self, article_urls)


    def parse_article(self, article_url):
        link, data = article_url
        guid = data["guid"]

        try:
            article = self.get_article(link)
        except Exception as e:
            logger.warn("Failed to parse article %s", link, exc_info=True)
            return

        if article is None: return

        article["title"] = data["title"]
        article["published"] = data["published"]
        article["source"] = "Monitor"
        article["source_url"] = link
        article["language"] = "si"
        # Generate ID from link
        article["id"] = get_sha_hash(guid)
        scraping.add_new_article(article)

    def get_article(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html

        tree = etree.fromstring(article_html, etree.HTMLParser())

        result["subtitles"] = [text.strip() for text in tree.xpath('//article/p[@class="uvod"]/text()')]

        # Sometimes they use bodytext for this
        text = tree.xpath('//article/p[@class="tekst"]//text()')
        if len(text) == 0:
            text = tree.xpath('//article/p[@class="bodytext"]/text()')

        result["text"] = '\n'.join(text)

        author = tree.xpath('//article/p[@class="bodyslika"]/span/text()')
        if len(author) > 0:
            result["author"] = (' '.join(author)).strip()
        else:
            result["author"] = None

        return result