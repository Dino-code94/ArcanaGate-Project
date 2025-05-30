import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('database.db')
new_password = generate_password_hash('securepassword123')

conn.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_password,))
conn.commit()
conn.close()

print("🔐 Password for 'admin' has been reset.")
