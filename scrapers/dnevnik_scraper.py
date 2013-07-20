import bs4
import feedparser
from scrapers.utils import time_to_datetime, get_hash, get_article

class DnevnikScraper(object):
    DNEVNIK_RSS_URL = "http://www.dnevnik.si/rss"

    def get_news(self, existing_ids=None):
        news = []
        feed_content = feedparser.parse(self.DNEVNIK_RSS_URL)

        max_counter = 30
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and get_hash(link) in existing_ids:
                print "Skipping", link
                continue

            article = self.get_article_text(link)
            if article is None: continue
            published_date = time_to_datetime(feed_entry["published_parsed"])
            article["published"] = published_date
            article["source"] = "Dnevnik"
            article["source_url"] = link
            article["language"] = "si"
            article["id"] = get_hash(link)
            news.append(article)

            max_counter -= 1
            if max_counter <= 0:
                break
        return news

    def get_article_text(self, link):
        print "[Dnevnik] Grabbing article", link
        article_html = get_article(link)
        result = {}

        article = bs4.BeautifulSoup(article_html)
        title = article.body.find(class_="title", text=True)

        if title is None:   # Some invalid links
            return None

        result["title"] = title.text.strip()
        
        author = article.body.find(class_="article-source")
        if author is not None and author.strong is not None:
            result["author"] = author.strong.text
        else:
            result["author"] = None

        subtitle = article.body.find('p', class_="intro-box", text=True)
        if subtitle is not None:
            result["subtitles"] = [subtitle.text.strip()]

        content = article.body.article
        if content is None:
            return None
        else:
            result["text"] = content.text.strip()
            return result
