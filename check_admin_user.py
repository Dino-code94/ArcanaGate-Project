import sqlite3

conn = sqlite3.connect('database.db')
user = conn.execute("SELECT id, username, is_admin FROM users WHERE username = ?", ('admin',)).fetchone()
conn.close()

print(user)