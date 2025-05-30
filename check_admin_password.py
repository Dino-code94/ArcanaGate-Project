import sqlite3
from werkzeug.security import check_password_hash

conn = sqlite3.connect('database.db')
row = conn.execute("SELECT password FROM users WHERE username = 'admin'").fetchone()
conn.close()

if row:
    stored_hash = row[0]
    password_ok = check_password_hash(stored_hash, 'securepassword123')
    print("✅ Password correct?" if password_ok else "❌ Wrong password")
else:
    print("User not found")
