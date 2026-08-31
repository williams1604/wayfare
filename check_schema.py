
import sqlite3

def check_schema():
    try:
        conn = sqlite3.connect('e:/wayfar/database.db')
        cursor = conn.cursor()
        
        print("Destinations Schema:")
        schema = cursor.execute("PRAGMA table_info(destinations)").fetchall()
        for col in schema:
            print(col)
            
        print("\nPackages Schema:")
        schema = cursor.execute("PRAGMA table_info(packages)").fetchall()
        for col in schema:
            print(col)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
