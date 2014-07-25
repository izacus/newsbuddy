import logging

import bs4
from scrapers.utils import get_rss, get_sha_hash, time_to_datetime, get_article


logger = logging.getLogger("scraper.val202")

class VAL202Scraper(object):

    VAL202_RSS_URL = "http://www.val202.si/feed/"

    def parse_source(self, existing_ids = None):
        article_urls = []
        feed_content = get_rss(self.VAL202_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            guid = feed_entry["guid"]
            if existing_ids and get_sha_hash(guid) in existing_ids:
                logger.debug("Skipping %s", guid)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            try:
                text = feed_entry["content"][0]["value"]
                # Strip HTML
                soup = bs4.BeautifulSoup(text)
                text = soup.text
            except KeyError:
                return

            title = feed_entry["title"]
            author = feed_entry.get("author", None)

            article_urls.append((link, {"guid": guid, "published": published_date, "title": title, "text": text, "author": author }))

        return article_urls

    def parse_article(self, article_url):
        link, data = article_url
        article = {}

        try:
            article_html = get_article(link)
            article["raw_html"] = article_html
        except Exception as e:
            logger.warn("Failed to parse article %s", link, exc_info=True)
            return


        article["text"] = data["text"]
        article["title"] = data["title"]
        article["published"] = data["published"]
        article["source"] = "Val202"
        article["source_url"] = link
        article["language"] = "si"
        article["author"] = data["author"]

        # Generate ID from link
        article["id"] = get_sha_hash(data["guid"])
        return article
