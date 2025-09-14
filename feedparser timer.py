import feedparser
import time

url = "https://feeds.megaphone.fm/GLT1412515089"

start_time = time.time()
try:
    feed = feedparser.parse(url)
except Exception as e:
    print(f"Error parsing feed: {e}")
    feed = None
end_time = time.time()

elapsed_time = end_time - start_time

print(f"Parsing took {elapsed_time:.4f} seconds.")
if feed:
    print(f"Feed title: {feed.feed.get('title', 'No title found')}")
    print(f"Number of entries: {len(feed.entries)}")
    # Print each entry safely
    for entry in feed.entries:
        try:
            print(str(entry).encode('utf-8', errors='replace').decode('utf-8'))
        except Exception as e:
            print(f"Error printing entry: {e}")
else:
    print("Feed could not be parsed.")