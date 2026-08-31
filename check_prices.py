
import sqlite3

try:
    conn = sqlite3.connect('e:/wayfar/database.db')
    cursor = conn.cursor()
    params = cursor.execute("SELECT name, price FROM packages").fetchall()
    for p in params:
        print(f"{p[0]}: {p[1]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
