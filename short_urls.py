import psycopg2
import datetime
from multiprocessing.pool import ThreadPool
from time import time as timer
from main import youtube_data
from urllib.request import urlopen

import time

start = time.time()

user = "dinesh" #Enter Your Username
conn = psycopg2.connect(database = "tweets", user = user, password = "", host = "127.0.0.1", port = "5432")
cur = conn.cursor()

print(datetime.datetime.now())
cur.execute("SELECT URL FROM SHORT_URLS GROUP BY URL")
records = cur.fetchall()
urls = []
for url in records:
    urls.append(url[0])


def fetch_url(url):
    try:
        response = urlopen(url, timeout = 2)
        return url, response.geturl(), None
    except Exception as e:
        return url, None, e


start = timer()
results = ThreadPool(30).imap_unordered(fetch_url, urls)
for url, redirect_url, error in results:
    if error is None:
        try:
            youtube_data(redirect_url)
        except Exception as e:
            print(e)
    else:
        pass
print("Elapsed Time: %s" % (timer() - start,))