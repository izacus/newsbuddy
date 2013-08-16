import bs4
import feedparser
from scrapers.utils import get_article, get_hash, time_to_datetime
import logging

logger = logging.getLogger("scraper.rtvslo")


class RTVScraper(object):
    RTV_RSS_URLS = ["http://www.rtvslo.si/feeds/01.xml", "http://www.rtvslo.si/feeds/16.xml", "http://www.rtvslo.si/feeds/04.xml",
                    "http://www.rtvslo.si/feeds/05.xml"]
    RTV_ARTICLE_URL = "http://www.rtvslo.si/index.php?c_mod=news&op=print&id="

    def get_news(self, existing_ids=None):
        news = []
        for rss_feed in self.RTV_RSS_URLS:
            logger.debug("Parsing %s", rss_feed)
            feed_content = feedparser.parse(rss_feed)
            for feed_entry in feed_content.entries:
                # Download article
                link = feed_entry["link"]

                if existing_ids and get_hash(link) in existing_ids:
                    logger.debug("Skipping %s", link)
                    continue

                article_id = link[link.rfind("/") + 1:]

                try:
                    news_item = self.get_article_text(article_id)
                except Exception as e:
                    logger.warn("Failed to parse article ID %s", article_id, exc_info=True)
                    continue

                published_date = time_to_datetime(feed_entry["published_parsed"])
                news_item["published"] = published_date
                news_item["source"] = "RTVSlo"
                news_item["source_url"] = link
                news_item["language"] = "si"
                news_item["author"] = None
                news_item["id"] = get_hash(link)
                news.append(news_item)
        return news

    def get_article_text(self, article_id):
        logger.debug("[RTVSlo] Grabbing article ID %s", article_id)
        article_html = get_article(self.RTV_ARTICLE_URL + str(article_id))
        result = {}
        article = bs4.BeautifulSoup(article_html)
        result["title"] = article.title.text

        subtitles = article.find_all("div", class_="subtitle")
        subtitles = [div.text for div in subtitles]
        result["subtitles"] = subtitles

        text_content = article.find_all("p")
        text_content = " ".join([p.text for p in text_content])
        result["text"] = text_content
        return result


