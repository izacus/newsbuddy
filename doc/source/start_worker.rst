Start worker
++++++++++++

Make sure you installed the buddy (see installation docs).

The worker is a python script that parses the RSS websites and artices.
Then populates SOLR and resets statistics in the web app.

To run the worker your solr and application must run.
After activating the virtualenv run::

    python work.py
