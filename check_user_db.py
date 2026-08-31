
import sqlite3
from werkzeug.security import check_password_hash

def check_user():
    conn = sqlite3.connect('e:/wayfar/database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    email = "newuser@example.com"
    user = cur.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    
    if user:
        print(f"User found: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"Hash: {user['password_hash']}")
        
        # Test password
        password = "password123"
        is_valid = check_password_hash(user["password_hash"], password)
        print(f"Password '{password}' is valid: {is_valid}")
    else:
        print("User NOT found in database")
        
    conn.close()

if __name__ == "__main__":
    check_user()
