# Check whats in the database
import sqlite3


conn = sqlite3.connect('feeds.db')
c = conn.cursor()

c.execute('''SELECT name FROM sqlite_master WHERE type='table';''')
tables = c.fetchall()

print("Tables in the database:")
for table in tables:
    print(table[0])

    c.execute(f'SELECT * FROM "{table[0]}" LIMIT 5;')
    rows = c.fetchall()

    print(f"First 5 entries in {table[0]}:")
    for row in rows:
        print(row)
