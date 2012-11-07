import calendar
from datetime import datetime
import hashlib
import bs4
import feedparser
import pytz
import requests

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
            published_st = feed_entry["published_parsed"]
            published_date = datetime.fromtimestamp(calendar.timegm(published_st), tz=pytz.utc)
            article["published"] = published_date
            article["source"] = "Zurnal24"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            hash = hashlib.md5()
            hash.update("Zurnal24")
            hash.update(link)
            article["id"] = hash.hexdigest()
            news.append(article)
        return news

    def get_article(self, article_id):
        print "[Zurnal] Grabbing article ID", article_id
        url = self.ZURNAL_PRINT_URL + str(article_id)
        response = requests.get(url)
        return response.text

    def get_article_text(self, article_id):
        article_html = self.get_article(article_id)
        result = {}
        article = bs4.BeautifulSoup(article_html)
        result["title"] = article.body.article.hgroup.h1.text

        content_div = article.find_all("div", class_="entry")
        result["text"] = content_div[0].text
        return result