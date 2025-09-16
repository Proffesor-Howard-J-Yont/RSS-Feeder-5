import sqlite3
import requests
import feedparser
import uuid

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

loading_bar = 0.00
loading_step = ""

def add_feed(feed_url):
    global loading_bar
    global loading_step

    try:
        loading_step = "Validating feed..."
        response = requests.head(feed_url, allow_redirects=True, timeout=5)
        if not 200 <= response.status_code < 400:
            print(f"HTTP error for {feed_url}. Status: {response.status_code}")
            return False
        loading_bar = 20.00

        loading_step = "Fetching feed content..."
        feed_content = requests.get(feed_url, timeout=5)
        loading_bar = 25.00

        loading_step = "Parsing feed..."
        feed = feedparser.parse(feed_content.text)
        if feed.bozo == 1:
            loading_step = f"Feed at {feed_url} is malformed or invalid. Error details: {feed.bozo_exception}"
            return
        loading_bar = 50.00

        loading_step = "Downloading feed cover art..."
        feed_image = None
        if 'image' in feed.feed and 'href' in feed.feed.image:
            image_url = feed.feed.image.href
            try:
                img_response = requests.get(image_url, timeout=5)
                if img_response.status_code == 200:
                    feed_image = img_response.content
            except requests.exceptions.RequestException as e:
                print(f"Failed to download feed image from {image_url}: {e}")
        loading_bar = 60.00

        loading_step = "Storing podcast in database..."
        table_name = str(uuid.uuid4())
        c.executemany('''INSERT OR IGNORE INTO feeds (table_name, name, description, image, feed_url, amt_clicked, auto_update, latest_clicked)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       [(table_name, feed.feed.title, feed.feed.description, feed_image, feed_url, 0, 0, None)])
        conn.commit()
        loading_bar = 75.00

        loading_step = "Storing podcast episodes..."
        # Quote the table name to avoid SQL errors
        c.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, description TEXT, audio_url TEXT, image_url TEXT, pub_date TIMESTAMP, downloaded BOOLEAN DEFAULT 0)')
        for entry in feed.entries:
            audio_url = None
            if 'enclosures' in entry and entry.enclosures:
                audio_url = entry.enclosures[0].href
            image_url = entry.get('image', {}).get('href', None)
            pub_date = entry.get('published', None)
            # Quote the table name here as well
            c.execute(f'''INSERT INTO "{table_name}" (title, description, audio_url, image_url, pub_date, downloaded)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                      (entry.title, entry.get('description', ''), audio_url, image_url, pub_date, 0))
            


    except requests.exceptions.RequestException as e:
        print(f"Connection error for {feed_url}: {e}")
        return False

