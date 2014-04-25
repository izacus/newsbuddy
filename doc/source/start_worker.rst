Start worker
++++++++++++

Make sure you installed the buddy (see installation docs).

The worker is a python script that parses the RSS websites and artices and populates SOLR and resets statistics in the web app. It should be run periodically for regular scraping.

To run the worker your Solr and WSGI application must run.

After activating the virtualenv run::

    python news_buddy/newsbuddy.py parse-news
