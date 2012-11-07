import calendar
from datetime import datetime
import hashlib
import bs4
import feedparser
import pytz
import requests

class DeloScraper(object):
    DELO_RSS_URL = "http://www.delo.si/rss/"

    def get_news(self):
        news = []
        feed_content = feedparser.parse(self.DELO_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            article = self.get_article_text(link)
            if article is None: continue

            published_st = feed_entry["published_parsed"]
            published_date = datetime.fromtimestamp(calendar.timegm(published_st), tz=pytz.utc)
            article["published"] = published_date
            article["source"] = "Delo"
            article["source_url"] = link
            article["language"] = "si"

            # Generate ID from link
            hash = hashlib.md5()
            hash.update("Delo")
            hash.update(link)
            article["id"] = hash.hexdigest()
            news.append(article)
        print news
        return news

    def get_article(self, link):
        print "[Delo] Grabbing article", link
        response = requests.get(link)
        return response.text

    def get_article_text(self, link):
        article_html = self.get_article(link)
        result = {}
        article = bs4.BeautifulSoup(article_html)
        result["title"] = article.title.text.strip()

        subtitle = article.find(id="EXCERPT", text=True)
        if subtitle is None:
            subtitle = article.find(id="EXCERPT_mnenja", text=True)

        if subtitle is not None:
            result["subtitles"] = [subtitle.text.strip()]

        content_item = article.find(id="D_NEWS")
        if content_item is None:
            content_item = article.find(id="D_NEWS_MNENJA")

        if content_item is not None:
            text_content = " ".join([p_item.text.strip() for p_item in content_item.find_all('p', text=True) if p_item is not None])
            result["text"] = text_content
            return result
        else:
            print "Unknown article content for", link
            return None

