import calendar
from datetime import datetime
import hashlib
import pytz
import requests

requests_session = requests.Session()

def get_article(url):
    response = requests_session.get(url)
    response.encoding = response.apparent_encoding
    return response.text

def get_hash(link):
    hash = hashlib.md5()
    hash.update(link)
    return hash.hexdigest()

def time_to_datetime(time):
    return datetime.fromtimestamp(calendar.timegm(time), tz=pytz.utc)