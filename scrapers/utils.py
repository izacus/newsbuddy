import calendar
from datetime import datetime
import hashlib
import pytz
import requests

def get_article(url):
    response = requests.get(url)
    return response.text

def get_hash(link):
    hash = hashlib.md5()
    hash.update(link)
    return hash.hexdigest()

def time_to_datetime(time):
    return datetime.fromtimestamp(calendar.timegm(time), tz=pytz.utc)