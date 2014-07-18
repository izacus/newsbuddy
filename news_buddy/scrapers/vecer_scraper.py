import logging
import bs4
import scraping
from scrapers.utils import time_to_datetime, get_hash, get_article, get_sha_hash, get_rss

logger = logging.getLogger("scraper.vecer")

class VecerScraper(object):

    VECER_RSS_URL = "http://mix.vecer.com/rss/"

    def parse_source(self, existing_ids=None):
        news = []
        feed_content = get_rss(self.VECER_RSS_URL)
        for feed_entry in feed_content.entries:
            link = feed_entry["link"]

            if existing_ids and get_sha_hash(link) in existing_ids:
                logger.debug("Skipping %s", link)
                continue

            published_date = time_to_datetime(feed_entry["published_parsed"])
            title = feed_entry["title"]

            news.append((link, {"published": published_date, "title": title}))

        scraping.parse_articles(self, news)


    def parse_article(self, article_url):
        link, data = article_url
        article = self.get_article(link)

        if article is None: return

        published_date = data["published"]
        article["title"] = data["title"]
        article["published"] = published_date
        article["source"] = "Vecer"
        article["source_url"] = link
        article["language"] = "si"
        # Generate ID from link
        article["id"] = get_sha_hash(link)
        scraping.add_new_article(article)

    def get_article(self, link):
        logger.debug("Grabbing article %s", link)

        article_html = get_article(link)
        result = {}
        result["raw_html"] = article_html
        article = bs4.BeautifulSoup(article_html)

        # Try to find the subtitle
        subtitle = article.find('font', size=3, color="#ff8000")
        if subtitle is not None and subtitle.find('b') is not None:
            result["subtitles"] = [subtitle.b.text.strip()]

        author = article.find('div', class_="clanekAVTOR")
        if author is not None:
            result["author"] = author.text.strip()
        else:
            result["author"] = None

        text_container = article.find(id="_xclaimwords_wrapper")
        if text_container is None:
            return None

        # Remove all script tags from text container
        scripts = text_container.findAll('script')
        [script.extract() for script in scripts]
        result["text"] = u" ".join(text_container.stripped_strings)
        return result