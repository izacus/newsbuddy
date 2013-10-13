# This is a bash script it needs to be extended to proper documentation or
# ansible recipe
set -e

# Create virtuaenv
virtualenv --no-site-packages .
source bin/activate
pip install -r requirements.txt


# you need git, gcc,  apache-maven and java (Oracle JDK)
# get solr tar.gz in ignore dir

# make a settings.py
cp settings.default.py settings.py

mkdir ignore
cd ignore

# get lemmetizer
git clone git@bitbucket.org:mavrik/slovene_lemmatizer.git

# build lemmatizer
cd slovene_lemmatizer
make
mvn compile

# cp so
cd bin
ln -s $(pwd)/libLemmatizer.so ../../

# lets make a jar
cd ..
cd target/classes
jar cf sl_lemmatizer-1.0.jar si
cd ../../..


# get solr
wget "http://archive.apache.org/dist/lucene/solr/4.5.0/solr-4.5.0.tgz" 
tar xvzf solr-4.5.0.tgz

# configure solr
cp -r  solr-4.5.0/example/solr/collection1/conf solr-4.5.0/example/solr/collection1/conf_backup
cp -r solr-4.5.0/example/solr .
##
rm solr/collection1/conf/schema.xml
rm solr/collection1/conf/solrconfig.xml
rm solr/collection1/conf/stopwords.txt
ln -s $(pwd)/../solr/config/* solr/collection1/conf/

mkdir solr/collection1/lib
cp slovene_lemmatizer/target/classes/sl_lemmatizer-1.0.jar solr/collection1/lib/

sed -i 's Users/jernej/Workspace/ '`pwd`'/ g' solr/collection1/conf/schema.xml

# configure settings.py
sed -i 's news collection1 g' ../settings.py

# run solr
cd solr-4.5.0/example
java -Dsolr.solr.home=../../solr -Djava.library.path=../..  -jar start.jar &
