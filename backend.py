import sqlite3
import requests
import feedparser
import uuid
import json
import sys  # Add this import at the top

conn = sqlite3.connect('feeds.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS feeds (
        table_name TEXT UNIQUE PRIMARY KEY,
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
        table_name = str(uuid.uuid4())
        c.executemany('''INSERT OR IGNORE INTO feeds (table_name, name, description, image, feed_url, amt_clicked, auto_update, latest_clicked)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       [(table_name, feed.feed.title, feed.feed.description, feed_image, feed_url, 0, 0, None)])
        conn.commit()

        update_progress(75, "Storing podcast episodes...")
        c.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, audio_url TEXT, image_url TEXT, pub_date TIMESTAMP, downloaded BOOLEAN DEFAULT 0)')
        conn.commit()
        num_entries = len(feed.entries)
        loading_increment = 25.00 / num_entries
        for entry in feed.entries:
            title = entry.title
            description = entry.summary if 'summary' in entry else ''
            cover_art_url = entry.image.href if 'image' in entry and 'href' in entry.image else (entry.itunes_image.href if 'itunes_image' in entry and 'href' in entry.itunes_image else None)
            audio_url = entry.enclosures[0].href if 'enclosures' in entry and len(entry.enclosures) > 0 else None
            pub_date = entry.published if 'published' in entry else None
            # clean up from unusable charachters (just in case) as well as clean up from /u200b, /u2060 charachter
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

            c.execute(f'''INSERT INTO "{table_name}" (title, description, audio_url, image_url, pub_date, downloaded)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                      (title, description, audio_url, cover_art_url, pub_date, 0))
            conn.commit()
            loading_bar = 75.00
            loading_bar += int(loading_increment)
    
    except requests.exceptions.RequestException as e:
        update_progress(0, f"Connection error: {str(e)}")
        return False

    update_progress(100, "Feed added successfully!")

# Add this at the bottom of the file
if __name__ == "__main__":
    if len(sys.argv) > 1:
        feed_url = sys.argv[1]
        add_feed(feed_url)
