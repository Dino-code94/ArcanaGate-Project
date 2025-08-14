import sqlite3

with sqlite3.connect("database.db") as conn:
    user = conn.execute(
        "SELECT id, username, is_admin "
        "FROM users "
        "WHERE username = ?",
        ('admin',)  
    ).fetchone()

print(user)
