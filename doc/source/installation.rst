Installation
++++++++++++

In order to install/run news_bunny you need:
- java
- gcc
- apache-maven
- python-virtualenv
- libmemcached


Basic setup
-----------

In the project directory run, to create a virtualenv::

    virtualenv --no-site-packages .
    source bin/activate

Then we need to install the dependencies::

    pip install -r requirements.txt


Copy the default project setting so we can modify them later::

    cp settings.default.py settings.py

In order to have lemmatizer/solr for development we make a ignore directory.
(ignored by git)::

    mkdir ignore

Lemmatizer install
------------------

Method A - use the lemmatizer bins shipped:

TODO

Method B- make the bins:

We clone the lemmatizer::

    cd ignore
    git clone git@bitbucket.org:mavrik/slovene_lemmatizer.git


Then we build it::

    cd slovene_lemmatizer
    make
    mvn compile


We link the lib and the so object to the ignore dir (so its more simple to find
it later)::

    cd ..
    ln $(pwd)/slovene_lemmatizer/bin/libLemmatizer.so
    ln $(pwd)/slovene_lemmatizer/bin/lemmatizer lemmatizer_lib

We need to create a JAR for the solr system::

    cd slovene_lemmatizer/target/classes
    jar cf sl_lemmatizer-1.0.jar si

Go back to ignore dir::

    cd ../../..

Sorl install
------------

First off all we need to get solr::

    wget "http://archive.apache.org/dist/lucene/solr/4.5.0/solr-4.5.0.tgz" 
    tar xvzf solr-4.5.0.tgz

Then we need to take the configurations with the project and replace them with
the solr defaults::

    cp -r  solr-4.5.0/example/solr/collection1/conf solr-4.5.0/example/solr/collection1/conf_backup
    cp -r solr-4.5.0/example/solr .
    ##
    rm solr/collection1/conf/schema.xml
    rm solr/collection1/conf/solrconfig.xml
    rm solr/collection1/conf/stopwords.txt
    ln -s $(pwd)/../solr/config/* solr/collection1/conf/


We need to add the slovene_lemmatizer solr plugin::

    mkdir solr/collection1/lib
    cp slovene_lemmatizer/target/classes/sl_lemmatizer-1.0.jar solr/collection1/lib/

We here are some configuraton changes.
The path to the lemmetizer .so from method B::

    sed -i 's Users/jernej/Workspace/ '`pwd`'/ g' solr/collection1/conf/schema.xml

The default solr core is collection1::

    sed -i 's news collection1 g' ../settings.py

Now we can run sorl::

    cd solr-4.5.0/example
    java -Dsolr.solr.home=../../solr -Djava.library.path=../..  -jar start.jar &

And go back to the root of the project::

    cd ../../..
