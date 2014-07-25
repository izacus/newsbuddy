import logging

from lxml import etree
from scrapers.utils import time_to_datetime, get_sha_hash, get_article, get_rss


logger = logging.getLogger("scraper.siol")

class SiolScraper(object):
    """
    Scraper contributed by Gasper Setinc
    """
    SIOL_RSS_URL = "http://www.siol.net/rss.aspx?path=SiOL.Net"

    def parse_source(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.SIOL_RSS_URL)

        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and get_sha_hash(link) in existing_ids:
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            title = feed_entry["title"]
            news.append((link, {"title": title, "published": published_date}))

        return news

    def parse_article(self, article_url):
        link, data = article_url

        article = self.get_article_text(link)

        if article is None: return
        published_date = data["published"]
        article["published"] = published_date
        article["title"] = data["title"]
        article["source"] = "Siol.net"
        article["source_url"] = link
        article["language"] = "si"
        article["id"] = get_sha_hash(link)
        return article

    def get_article_text(self, link):
        logger.debug("Grabbing article %s", link)
        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
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

        try:
            result["subtitles"] = [' '.join(tree.xpath('//article[@id="article"]/header')[0].xpath('./p')[-1].xpath('./text()')).strip()]
        except IndexError:
            result["subtitles"] = None

        result["text"] = '\n\n'.join([' '.join(x).strip() for x in map(lambda x: x.xpath('.//text()'), tree.xpath('//article[@id="article"]/p'))]).strip()

        return result