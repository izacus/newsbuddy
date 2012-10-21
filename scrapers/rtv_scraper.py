import calendar
import bs4
import pytz
import feedparser
import requests
import hashlib
from time import mktime
from datetime import datetime

class RTVScraper(object):
    RTV_RSS_URLS = ["http://www.rtvslo.si/feeds/01.xml", "http://www.rtvslo.si/feeds/16.xml", "http://www.rtvslo.si/feeds/04.xml",
                    "http://www.rtvslo.si/feeds/05.xml"]
    RTV_ARTICLE_URL = "http://www.rtvslo.si/index.php?c_mod=news&op=print&id="

    def get_news(self):
        news = []
        for rss_feed in self.RTV_RSS_URLS:
            print "Parsing", rss_feed
            feed_content = feedparser.parse(rss_feed)
            for feed_entry in feed_content.entries:
                # Download article
                link = feed_entry["link"]
                article_id = link[link.rfind("/") + 1:]
                news_item = self.get_article_text(article_id)

                published_st = feed_entry["published_parsed"]
                # Convert struct_time to datetime
                published_date = datetime.fromtimestamp(calendar.timegm(published_st), tz=pytz.utc)
                news_item["published"] = published_date
                news_item["source"] = "RTVSlo"
                news_item["source_url"] = link
                news_item["language"] = "si"

                # Generate ID from link
                hash = hashlib.md5()
                hash.update("RTVSlo")
                hash.update(link)
                news_item["id"] = hash.hexdigest()
                news.append(news_item)
        return news

    def get_article(self, article_id):
        print "Grabbing article ID", article_id
        url = self.RTV_ARTICLE_URL + str(article_id)
        response = requests.get(url)
        return response.text

    def get_article_text(self, article_id):
        article_html = self.get_article(article_id)
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


