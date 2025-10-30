import sqlite3
import requests
import feedparser
import json
import sys  # Add this import at the top

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

global loading_bar
global loading_step
loading_bar = 0.00
loading_step = "Warming up..."

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
    # Skip the first one (top 1) and return the next 5
    return c.fetchall()[1:11]

def search_feeds(query):
    like_query = f"%{query}%"
    if query.strip() == "":
        return []
    c.execute("SELECT name, description, feed_url, amt_clicked FROM feeds WHERE name LIKE ? OR description LIKE ? LIMIT 20", (like_query, like_query))
    return c.fetchall()

# Add this at the bottom of the file
if __name__ == "__main__":
    if len(sys.argv) > 1:
        feed_url = sys.argv[1]
        add_feed(feed_url)
