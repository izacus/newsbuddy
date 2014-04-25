import logging
from lxml import etree
from scrapers.utils import get_rss, get_sha_hash, time_to_datetime, get_article

logger = logging.getLogger("scraper.monitor")

class MonitorScraper(object):

    MONITOR_RSS_URL = "http://www.monitor.si/media/rss/rss-fb-monitor-novice.xml"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.MONITOR_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            guid = feed_entry["guid"]
            if existing_ids and get_sha_hash(guid) in existing_ids:
                logger.debug("Skipping %s", guid)
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
            article["source"] = "Monitor"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            article["id"] = get_sha_hash(guid)
            news.append(article)
        return news

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