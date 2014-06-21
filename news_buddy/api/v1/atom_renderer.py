import datetime
import urllib
from flask.ext.api.renderers import BaseRenderer
from pyatom import AtomFeed
import settings

class AtomRenderer(BaseRenderer):
    media_type = "application/atom+xml"

    def add_feed_items(self, feed, results):

        for result in results:

            published = datetime.datetime.strptime(result['published'], "%Y-%m-%dT%H:%M:%SZ")#[:6]

            if 'snippet' in result:
                summary = ''.join('<p>' + p + '</p>' for p in result['snippet'])
            else:
                summary = None

            feed.add(title=result['title'],
                     title_type='html',

                     author=result['source'],
                     url=result['link'],

                     # Ideally this should be date of crawling (or something).
                     updated=published,
                     published=published,

                     content=result.get('content'),
                     content_type='html',

                     summary=summary,
                     summary_type='html',
                     )

    def render(self, data, media_type, **options):
        title = u'Novi\u010dar'

        # I'm sure this could be done better...
        page_url = settings.LOCAL_URL + "#!/latest"

        if "query" in data:
            query = data["query"]
            if isinstance(query, unicode):
                query = query.encode("utf8")

            urlencoded_query = urllib.quote(query)
            page_url += "#" + urlencoded_query
            url = settings.LOCAL_URL + '/v1/news/latest/?q=' + urlencoded_query
            title = data["query"].strip() + " - " + title
        else:
            url = settings.LOCAL_URL + '/v1/news/latest/'

        # It would be nice to know time of last crawl, so that the "updated"
        # field for the feed could be set.
        feed = AtomFeed(title=title,
                        url=page_url,
                        feed_url=url)

        if 'results' in data:
            self.add_feed_items(feed, data['results'])

        return feed.to_string()

class AtomXMLRenderer(AtomRenderer):
    media_type = "application/xml"