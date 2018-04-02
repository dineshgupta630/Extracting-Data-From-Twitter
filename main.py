import ijson
import re
import psycopg2
import requests
from urllib.parse import urlparse, parse_qs
from requests_futures.sessions import FuturesSession

#Enter Your Username
user = "dinesh"
conn = psycopg2.connect(database = "tweets", user = user, password = "", host = "127.0.0.1", port = "5432")
cur = conn.cursor()
session = FuturesSession()


try:
    cur.execute('''CREATE TABLE VIDEO_DATA
            (YOUTUBE_ID TEXT PRIMARY KEY     NOT NULL,
            VIEWS            BIGINT,
            LIKES     BIGINT,
            DISLIKES BIGINT,
            COMMENTS INT,
            NO INT);''')
    conn.commit()

    # cur.execute('''CREATE TABLE TWEET_DATA
    #         (TWEET_ID BIGINT PRIMARY KEY     NOT NULL,
    #         DONE INT);''')
    # conn.commit()

    cur.execute('''CREATE TABLE SHORT_URLS
            (URL TEXT     NOT NULL);''')
    conn.commit()

except Exception as e:
    print(e)
    conn.rollback()


def youtube_data(url):
    data = youtube_url_or_not(url)
    if data:
        print("YouTube")
        video = video_id(data.group())
        if video:
            key = 'AIzaSyAOe6Qx_bKox4v8_s_Kd0TpDS6xRGxocFU'
            r = requests.get(
                'https://www.googleapis.com/youtube/v3/videos?part=statistics&id=' + video + '&key=' + key)
            statistics = r.json()
            no = int(1)
            if bool(statistics['items']):
                view_count = statistics['items'][0]['statistics']['viewCount']
                likes = statistics['items'][0]['statistics']['likeCount']
                dislikes = statistics['items'][0]['statistics']['dislikeCount']
                comments = statistics['items'][0]['statistics']['commentCount']
                store_video_data(video, view_count, likes, dislikes, comments, no)
            else:
                invalid_video_data(video, no)


def store_video_data(video, view_count, likes, dislikes, comments, no):
    """
    :param video:
    :param view_count:
    :param likes:
    :param dislikes:
    :param comments:
    :param no:
    """
    try:
        query = '''
           INSERT INTO VIDEOS_DATA (YOUTUBE_ID,VIEWS, LIKES, DISLIKES, COMMENTS, NO)
                VALUES (%s, %s, %s, %s, %s, %s::int)
                ON CONFLICT (YOUTUBE_ID)
                DO UPDATE SET
                    VIEWS = EXCLUDED.VIEWS,
                    LIKES = EXCLUDED.LIKES,
                    DISLIKES =  EXCLUDED.DISLIKES,
                    COMMENTS = EXCLUDED.COMMENTS,
                    NO = EXCLUDED.NO + 1;
        '''
        values = (video, view_count, likes, dislikes, comments, no)
        cur.execute(query, values)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()


def invalid_video_data(video, no):
    """
    :param video:
    :param no:
    """
    try:
        invalid_query = '''
           INSERT INTO VIDEOS_DATA (YOUTUBE_ID, NO, INVALID)
                VALUES (%s, %s, %s)
                ON CONFLICT (YOUTUBE_ID)
                DO UPDATE SET
                    NO = EXCLUDED.NO + 1;
        '''
        invalid_values = (video, no, 1)
        cur.execute(invalid_query, invalid_values)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()


def video_id(youtube_url):
    """
    :param youtube_url:
    :return: YouTube video ID
    """
    try:
        query = urlparse(youtube_url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None
    except Exception as e:
        print(e)
        return None


def youtube_url_or_not(url):
    """
    :param url:
    :return: if is a YouTube video
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, str(url))
    if youtube_regex_match:
        return youtube_regex_match


def main():
    input_file = 'sample_tweets_data.json'
    file = open(input_file)
    parser = ijson.parse(file)
    for prefix, event, value in parser:
        if prefix == "item.entities.urls.item.expanded_url":
            try:
                query = urlparse(value)
                if query.hostname in ('bit.ly', 'goo.gl'):
                    try:
                        cur.execute("""INSERT INTO SHORT_URLS (URL) VALUES (%s)""", (value,))
                        conn.commit()
                    except Exception as e:
                        print(e)
                        conn.rollback()
                else:
                    youtube_data(value)
            except UnicodeEncodeError:
                print('Unicode Error')
            except Exception as e:
                print(e)
                conn.rollback()


if __name__ == "__main__":
    main()