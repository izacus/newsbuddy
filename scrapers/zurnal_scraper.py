import bs4
import feedparser
from scrapers.utils import get_article, get_hash, time_to_datetime

class ZurnalScraper(object):

    ZURNAL_RSS_URL = "http://www.zurnal24.si/index.php?ctl=show_rss&url_alias=novice"
    ZURNAL_PRINT_URL = "http://www.zurnal24.si/print/"

    def get_news(self):
        news = []
        feed_content = feedparser.parse(self.ZURNAL_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            article_id = link[link.rfind("-") + 1:]
            article = self.get_article_text(article_id)
            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["published"] = published_date
            article["source"] = "Zurnal24"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            article["id"] = get_hash(link)
            news.append(article)
        return news

    def get_article_text(self, article_id):
        print "[Zurnal] Grabbing article ID", article_id
        article_html = get_article(self.ZURNAL_PRINT_URL + str(article_id))
        result = {}
        article = bs4.BeautifulSoup(article_html)
        result["title"] = article.body.article.hgroup.h1.text
        content_div = article.find_all("div", class_="entry")
        result["text"] = content_div[0].text
        return result