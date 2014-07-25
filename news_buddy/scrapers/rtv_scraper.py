import logging

import bs4
from scrapers.utils import get_article, get_hash, time_to_datetime, get_sha_hash, get_rss


logger = logging.getLogger("scraper.rtvslo")


class RTVScraper(object):
    RTV_RSS_URLS = ["http://www.rtvslo.si/feeds/01.xml", "http://www.rtvslo.si/feeds/16.xml", "http://www.rtvslo.si/feeds/04.xml",
                    "http://www.rtvslo.si/feeds/05.xml"]
    RTV_ARTICLE_URL = "http://www.rtvslo.si/index.php?c_mod=news&op=print&id="

    def parse_source(self, existing_ids=None):
        news = []
        for rss_feed in self.RTV_RSS_URLS:
            logger.debug("Parsing %s", rss_feed)
            feed_content = get_rss(rss_feed)
            for feed_entry in feed_content.entries:
                # Download article
                link = feed_entry["link"]

                if existing_ids and (get_hash(link) in existing_ids or get_sha_hash(link) in existing_ids):
                    logger.debug("Skipping %s", link)
                    continue

                published_date = time_to_datetime(feed_entry["published_parsed"])
                news.append((link, {"published": published_date}))

        return news

    def parse_article(self, article_url):
        link, data = article_url
        article_id = link[link.rfind("/") + 1:]

        news_item = self.get_article_text(article_id)
        published_date = data["published"]
        news_item["published"] = published_date
        news_item["source"] = "RTVSlo"
        news_item["source_url"] = link
        news_item["language"] = "si"
        news_item["author"] = None
        news_item["id"] = get_sha_hash(link)
        return news_item

    def get_article_text(self, article_id):
        logger.debug("[RTVSlo] Grabbing article ID %s", article_id)
        article_html = get_article(self.RTV_ARTICLE_URL + str(article_id))
        result = {}
        result["raw_html"] = article_html
        article = bs4.BeautifulSoup(article_html)
        result["title"] = article.title.text.strip()

        subtitles = article.find_all("div", class_="subtitle")
        subtitles = [div.text for div in subtitles]
        result["subtitles"] = subtitles

        text_content = article.find_all("p")
        text_content = u"\n".join([u" ".join(p.stripped_strings) for p in text_content])

        result["text"] = text_content
        return result


