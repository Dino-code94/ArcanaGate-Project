import sqlite3

conn = sqlite3.connect('database.db')
conn.execute("DELETE FROM users WHERE username = 'admin'")
conn.commit()
conn.close()

print("🗑️ Admin user deleted.")
