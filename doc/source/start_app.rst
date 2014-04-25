Application start
+++++++++++++++++

To start this application solr must be running.

The application is the main pyramid web application which provides web interface and search functionality.

Development server
-------------------

To start the development server run run::

    python news_buddy/newsbuddy.py runserver

This will start server on port 8005.

Production server
-------------------

Production deployment should be run within a WSGi server. See "Production setup with WSGi server" in install docs for instructions on how to create an INI file for that kind of server.
