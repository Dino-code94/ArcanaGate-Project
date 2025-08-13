import sqlite3
from werkzeug.security import generate_password_hash

USERNAME = "dino"
NEW_PASSWORD = "jesusofsuburbia"

with sqlite3.connect("database.db") as conn:
    hashed = generate_password_hash(NEW_PASSWORD)

    cur = conn.execute(
        "UPDATE users SET password = ?, is_admin = 1 "
        "WHERE username = ?",
        (hashed, USERNAME),
    )
    if cur.rowcount == 0:
        conn.execute(
            "INSERT INTO users (username, password, is_admin) "
            "VALUES (?, ?, 1)",
            (USERNAME, hashed),
        )
    conn.commit()

print(f"✅ Password reset for: {USERNAME}")
