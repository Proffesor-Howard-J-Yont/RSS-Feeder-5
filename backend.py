import sqlite3
import requests
import feedparser
import json
import io
import os
import sys
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, PictureType, Encoding, COMM, USLT
import mutagen
import re
from notifypy import Notify

conn = sqlite3.connect('feeds.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS feeds (
        name TEXT NOT NULL,
        description TEXT,
        image BLOB,
        feed_url TEXT NOT NULL UNIQUE,
        amt_clicked INTEGER DEFAULT 0,
        auto_update BOOLEAN DEFAULT 0,
        latest_clicked TIMESTAMP
    )
''')
conn.commit()

def update_progress(progress, step):
    with open('progress.json', 'w') as f:
        json.dump({"progress": progress, "step": step}, f)

def add_feed(feed_url):
    try:
        update_progress(0, "Starting...")

        update_progress(10, "Validating feed...")
        response = requests.head(feed_url, allow_redirects=True, timeout=5)
        if not 200 <= response.status_code < 400:
            print(f"HTTP error for {feed_url}. Status: {response.status_code}")
            return False

        update_progress(20, "Fetching feed content...")
        feed_content = requests.get(feed_url, timeout=15)

        update_progress(30, "Parsing feed...")
        feed = feedparser.parse(feed_content.text)
        if feed.bozo == 1:
            update_progress(0, f"Feed at {feed_url} is malformed or invalid")
            return

        update_progress(50, "Downloading feed cover art...")
        feed_image = None
        if 'image' in feed.feed and 'href' in feed.feed.image:
            image_url = feed.feed.image.href
            try:
                img_response = requests.get(image_url, timeout=5)
                if img_response.status_code == 200:
                    feed_image = img_response.content
            except requests.exceptions.RequestException as e:
                print(f"Failed to download feed image from {image_url}: {e}")

        update_progress(60, "Storing podcast in database...")
        c.executemany('''INSERT OR IGNORE INTO feeds (name, description, image, feed_url, amt_clicked, latest_clicked)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                       [(feed.feed.title, feed.feed.description, feed_image, feed_url, 0, None)])
        conn.commit()
    
    except requests.exceptions.RequestException as e:
        update_progress(0, f"Connection error: {str(e)}")
        return False

    update_progress(100, "Feed added successfully!")

def clean_up_feed(entry):
    title = entry.title
    description = entry.summary if 'summary' in entry else ''
    cover_art_url = entry.image.href if 'image' in entry and 'href' in entry.image else (entry.itunes_image.href if 'itunes_image' in entry and 'href' in entry.itunes_image else None)
    audio_url = entry.enclosures[0].href if 'enclosures' in entry and len(entry.enclosures) > 0 else None
    pub_date = entry.published if 'published' in entry else None

    title = title.replace('\u200b', '').strip()
    title = title.replace('\u2060', '').strip()
    title = title.replace('\ufeff', "").strip()
    description = description.replace('\u200b', '').strip()
    description = description.replace('\u2060', '').strip()
    description = description.replace('\ufeff', "").strip()
    if cover_art_url:
        cover_art_url = cover_art_url.replace('\u200b', '').strip()
        cover_art_url = cover_art_url.replace('\u2060', '').strip()
        cover_art_url = cover_art_url.replace('\ufeff', "").strip()
    if audio_url:
        audio_url = audio_url.replace('\u200b', '').strip()
        audio_url = audio_url.replace('\u2060', '').strip()
        audio_url = audio_url.replace('\ufeff', "").strip()
    if pub_date:
        pub_date = pub_date.replace('\u200b', '').strip()
        pub_date = pub_date.replace('\u2060', '').strip()
        pub_date = pub_date.replace('\ufeff', "").strip()
    return title, description, cover_art_url, audio_url, pub_date

def grab_top_1_podcast():
    c.execute("SELECT name, description, feed_url, amt_clicked FROM feeds ORDER BY amt_clicked DESC LIMIT 1")
    return c.fetchall()

def get_feed_details(feed_url):
    c.execute("SELECT name, description, feed_url, amt_clicked FROM feeds WHERE feed_url = ?", (feed_url,))
    return c.fetchall()

def get_episodes_for_feed(feed_url, start_index=0, end_index=20):
    # rewrite to fetch episodes from feedparser instead of DB
    feed = feedparser.parse(feed_url)
    episodes = []
    for entry in feed.entries[start_index:end_index]:
        title, description, cover_art_url, audio_url, pub_date = clean_up_feed(entry)
        episodes.append((title, description, audio_url, cover_art_url, pub_date))
    return episodes

    # # Get the table name for the feed
    # c.execute("SELECT table_name FROM feeds WHERE feed_url = ?" , (feed_url,))
    # result = c.fetchone()
    # if not result:
    #     return []
    # table_name = result[0]
    # c.execute(f'SELECT title, description, audio_url, image_url, datetime(pub_date), downloaded FROM "{table_name}" ORDER BY datetime(pub_date) DESC, id DESC')
    # return c.fetchall()

def grab_top_10_podcasts():
    c.execute("SELECT name, description, feed_url, amt_clicked FROM feeds ORDER BY amt_clicked DESC LIMIT 11")
    # Skip the first one (top 1) and return the next 10
    return c.fetchall()[1:11]

def search_feeds(query):
    like_query = f"%{query}%"
    if query.strip() == "":
        return []
    c.execute("SELECT name, description, feed_url, amt_clicked FROM feeds WHERE name LIKE ? OR description LIKE ? LIMIT 20", (like_query, like_query))
    return c.fetchall()

def download_episode(feed_url, index):
    def sanitize_filename(name):
        return re.sub(r'[\\/*?:"<>|]', "", name)

    feed = feedparser.parse(feed_url)
    podcast_name = feed.feed.title
    episode_title, description, cover_art_url, audio_url, pub_date = clean_up_feed(feed.entries[index])

    try:
        audio_response = requests.get(audio_url, stream=True)
        audio_response.raise_for_status()

        total_size = int(audio_response.headers.get('content-length', 0))
        downloaded_size = 0

        sanitized_podcast_name = sanitize_filename(podcast_name)
        sanitized_episode_title = sanitize_filename(episode_title)

        podcast_dir = os.path.join(os.getcwd(), 'Podcasts', sanitized_podcast_name)
        os.makedirs(podcast_dir, exist_ok=True)

        file_path = os.path.join(podcast_dir, f"{sanitized_episode_title}.mp3")
        with open(file_path, 'wb') as f:
            for chunk in audio_response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    progress = downloaded_size / total_size if total_size else 0
                    update_progress(progress * 100, f"Downloading {episode_title}...")
        try:
            audio = MP3(file_path, ID3=ID3)
            try:
                audio.add_tags()
            except mutagen.id3.error:
                pass
            try:
                easy_tags = EasyID3(file_path)
            except mutagen.id3.ID3NoHeaderError:
                easy_tags = mutagen.File(file_path, easy=True)
                easy_tags.add_tags()
            easy_tags["title"] = episode_title
            easy_tags["artist"] = podcast_name
            easy_tags.save()
            if cover_art_url:
                try:
                    image_response = requests.get(cover_art_url)
                    image_data = image_response.content
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Cover',
                            data=image_data
                        )
                    )
                except Exception as e:
                    print(f"Error fetching episode image for metadata: {e}")
            audio.save()
        except Exception as e:
            print(f"Error adding metadata: {e}")

        notification = Notify()
        notification.title = "Download Complete"
        notification.message = f"{episode_title} has been downloaded."
        notification.send()

    except Exception as e:
        print(f"Error downloading episode: {e}")

# Add this at the bottom of the file
if __name__ == "__main__":
    if len(sys.argv) > 1:
        feed_url = sys.argv[1]
        add_feed(feed_url)
