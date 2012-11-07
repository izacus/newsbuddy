import calendar
from datetime import datetime
import hashlib
import bs4
import feedparser
import pytz
import requests

class DnevnikScraper(object):
    DNEVNIK_RSS_URL = "http://www.dnevnik.si/rss"

    def get_news(self):
        news = []
        feed_content = feedparser.parse(self.DNEVNIK_RSS_URL)

        max_counter = 30
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            article = self.get_article_text(link)
            if article is None: continue

            published_st = feed_entry["published_parsed"]
            published_date = datetime.fromtimestamp(calendar.timegm(published_st), tz=pytz.utc)
            article["published"] = published_date
            article["source"] = "Dnevnik"
            article["source_url"] = link
            article["language"] = "si"
            # Generate ID from link
            hash = hashlib.md5()
            hash.update("Dnevnik")
            hash.update(link)
            article["id"] = hash.hexdigest()
            news.append(article)

            max_counter -= 1
            if max_counter <= 0:
                break
        return news

    def get_article(self, link):
        print "[Dnevnik] Grabbing article", link
        response = requests.get(link)
        return response.text

    def get_article_text(self, link):
        article_html = self.get_article(link)
        result = {}

        article = bs4.BeautifulSoup(article_html)
        title = article.body.find(class_="title", text=True)

        if title is None:   # Some invalid links
            return None

        result["title"] = title.text.strip()

        subtitle = article.body.find('p', class_="intro-box", text=True)
        if subtitle is not None:
            result["subtitles"] = [subtitle.text.strip()]

        content = article.body.article
        if content is None:
            return None
        else:
            result["text"] = content.text.strip()
            return result