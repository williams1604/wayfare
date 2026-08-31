
import sqlite3

try:
    conn = sqlite3.connect('e:/wayfar/database.db')
    cursor = conn.cursor()
    params = cursor.execute("SELECT name, image_url FROM packages WHERE name IN ('New York Skyline', 'Dubai Desert Safari')").fetchall()
    print(params)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
