Installation
++++++++++++

In order to install/run Newsbuddy you need:

- Python 2.6 or newer
- PostgreSQL database 9.x or newer
- Java 1.6 or newer
- (optional) memcached cache server


Standalone Solr installation
-------------------
While it is STRONGLY recommended for Solr to be deployed in a proper servlet container (e.g. Tomcat, Glassfish, etc.), using standalone Jetty is perfectly fine for development purposes.

Newsbuddy requires a recent Solr installation with Lemmagen slovenian langauge lemmatizer for stemming.

1. Get and unpack Solr from `Solr Homepage <http://lucene.apache.org/solr/mirrors-solr-redir.html>`_
2. Create Solr Home directory, which will hold Solr database, configuration and Newsbuddy index::

    mkdir ~/solr_home

3. Copy pre-made solr.xml file from unpacked distribution::

    cp ./solr-4.6.0/solr/solr.xml ~/solr_home

4. Download `Lemmagen lemmatizer JAR file <https://bitbucket.org/mavrik/slovene_lemmatizer/downloads/lemmatizer_solr_1.1.jar>`_ and copy it into lib subfolder of home directory::

    mkdir ~/solr_home/lib
    wget https://bitbucket.org/mavrik/slovene_lemmatizer/downloads/lemmatizer_solr_1.1.jar
    cp lemmatizer_solr_1.1.jar ~/solr_home/lib

5. Create Newsbuddy Solr core and copy core configuration files from Newsbuddy source::

    mkdir ~/solr_home/news
    touch ~/solr_home/news/core.properties
    mkdir ~/solr_home/news/conf
    cp -rv news-buddy/solr/config/* ~/solr_home/news/conf/

6. Start Solr with start.jar in unpacked directory with solr_home directory as solr.solr.home parameter::

    java -Xmx2G -Dsolr.solr.home=~/solr_home/ -jar ./solr-4.6.0/start.jar &

 Solr startup must execute without any exceptions. Output log must include::

    INFO  si.virag.solr.LemmagenLemmatizer  – Initialized lemmatizer with language mlteast-sl

 which shows proper lemmatizer configuration.


Newsbuddy setup
-----------

Install required memcached lib first (needed even if you won't use memcached)::

    apt-get install libmemcached-dev

In the project directory run, to create a virtualenv::

    virtualenv --no-site-packages .
    source bin/activate

Then we need to install the dependencies::

    pip install -r requirements.txt


Copy the default project setting so we can modify them later::

    cp settings.default.py settings.py

Setup database
~~~~~~~~~~~~~~~~

Create a database for newsbuddy in your Postgresql and give proper permissions to user.

Updated settings.py with connection string to your database::

   DB_CONNECTION_STRING = "postgresql://DATABASE_HOST/DATABASE_NAME"

e.g.::

   DB_CONNECTION_STRING = "postgresql://localhost/news"


Setup Solr endpoint
~~~~~~~~~~~~~~~~~~~~~~

Set Solr HTTP endpoint. If you followed instructions at the start of this document your Solr endpoint configuration will be::

    SOLR_ENDPOINT_URLS = { "si" : "http://localhost:8983/solr/news/"}
    SOLR_DEFAULT_ENDPOINT = "si"

Setup local path
~~~~~~~~~~~~~~~~~~~~~

Setup LOCAL_URL variable to show to newsbuddy HTTP path. Make sure the URL works from local machine. If you're running a development server the value will be::

    LOCAL_URL = "http://localhost:8005"

(Optional) Setup memcached
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Newsbuddy performs better with memcached caching server. Install it on your distribution, then updated MEMCACHED_URL variable to point to your server instance::

    MEMCACHED_URL = "127.0.0.1"

(Optional) Compile minified JavaScript
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minifying JavaScript increases Newsbuddy performance on the clientside. For JS compilation you will need:

- node.js
- Grunt

Before running grunt on newsbuddy for the first time::

    npm install

To compile JS run::

    grunt

in toplevel Newsbuddy directory. This will compile and minify JS files into ui/dist/nb.min.js file.

Production setup with WSGi server
-----------------------------------

If you with to run newsbuddy in production with WSGi server, follow steps in previous section, then copy production WSGi configuration file::

    cp production.default.ini production.ini

and update paths to newsbuddy in that file:

    chdir = /home/newsbuddy/news-buddy
    virtualenv = /home/newsbuddy/news-buddy

INI file can then be used as a parameter for WSGi server.
