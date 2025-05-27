import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Add is_admin column (0 = regular user, 1 = admin)
c.execute('''
ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0
''')

conn.commit()
conn.close()
print("✅ is_admin column added.")
