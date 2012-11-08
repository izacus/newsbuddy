import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_article

class DeloScraper(object):
    DELO_RSS_URL = "http://www.delo.si/rss/"

    def get_news(self):
        news = []
        feed_content = feedparser.parse(self.DELO_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]
            article = self.get_article_text(link)
            if article is None: continue
            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["published"] = published_date
            article["source"] = "Delo"
            article["source_url"] = link
            article["language"] = "si"
            article["id"] = get_hash(link)
            news.append(article)
        print news
        return news

    def get_article_text(self, link):
        print "[Delo] Grabbing article", link
        article_html = get_article(link)
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

