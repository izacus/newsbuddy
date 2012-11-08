import bs4
import feedparser
from scrapers.utils import get_article, get_hash, time_to_datetime

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
                published_date = time_to_datetime(feed_entry["published_parsed"])
                news_item["published"] = published_date
                news_item["source"] = "RTVSlo"
                news_item["source_url"] = link
                news_item["language"] = "si"
                news_item["id"] = get_hash(link)
                news.append(news_item)
        return news

    def get_article_text(self, article_id):
        print "[RTVSlo] Grabbing article ID", article_id
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


