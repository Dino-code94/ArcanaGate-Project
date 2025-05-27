import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
c = conn.cursor()

username = 'admin'
password = generate_password_hash('supersecure123')  # change this if you want
is_admin = 1  # This marks the user as an admin

try:
    c.execute('''
    INSERT INTO users (username, password, is_admin)
    VALUES (?, ?, ?)
    ''', (username, password, is_admin))
    conn.commit()
    print("✅ Admin user created.")
except sqlite3.IntegrityError:
    print("⚠️ Username already exists.")
finally:
    conn.close()
