import calendar
from datetime import datetime
import hashlib
from urllib2 import ProxyHandler
import sys

import feedparser
import pytz
import requests


requests_session = requests.Session()

# Proxy detection is broken on OS X 10.9 in python currently causing the process to hang
# Hence we disable all proxy detection code in Requests and urllib2-related calls here
if sys.platform == "darwin":
    requests_session.trust_env = False

def get_rss(url):

    if sys.platform == "darwin":
        return feedparser.parse(url, handlers=[ProxyHandler(proxies={})])
    else:
        return feedparser.parse(url)

def get_article(url):
    if sys.platform == "darwin":
        response = requests_session.get(url, proxies={})
    else:
        response = requests_session.get(url)
    response.encoding = response.apparent_encoding
    return response.text

def get_hash(link):
    hash = hashlib.md5()
    hash.update(link)
    return hash.hexdigest()

def get_sha_hash(link):
    hash = hashlib.sha512()
    hash.update(link)
    return hash.hexdigest()

def time_to_datetime(time):
    return datetime.fromtimestamp(calendar.timegm(time), tz=pytz.utc)