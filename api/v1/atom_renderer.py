import datetime
import time
from pyatom import AtomFeed


class AtomRenderer(object):

    acceptable = ('application/atom+xml', 'application/xml')

    def __init__(self, info):
        pass

    def add_feed_items(self, feed, results):

        for result in results:

            published = datetime.datetime(*time.strptime(result['published'], "%Y-%m-%dT%H:%M:%SZ")[:6])

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

    def __call__(self, data, context):
        request = context['request']
        response = request.response

        response.content_type = context['request'].accept.best_match(self.acceptable)
        if not response.content_type:
            response.content_type = self.acceptable[0]

        title = u'Novi\u010dar'

        # I'm sure this could be done better...
        url = request.host_url + '#!/latest'

        query = request.GET.get('q')
        if query:
            title = query.strip() + " - " + title
            url += '#' + query

        # It would be nice to know time of last crawl, so that the "updated"
        # field for the feed could be set.
        feed = AtomFeed(title=title,
                        url=url,
                        feed_url=request.url)

        if 'results' in data:
            self.add_feed_items(feed, data['results'])

        return feed.to_string()