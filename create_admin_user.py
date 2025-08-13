import sqlite3
from werkzeug.security import generate_password_hash

USERNAME = "dino"
PLAINTEXT = "jesusofsuburbia"

with sqlite3.connect("database.db") as conn:
    # Ensure username is unique (safe to run repeatedly)
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username "
        "ON users(username)"
    )

    hashed = generate_password_hash(PLAINTEXT)

    # Upsert admin user with this password
    conn.execute(
        "INSERT INTO users (username, password, is_admin) "
        "VALUES (?, ?, 1) "
        "ON CONFLICT(username) DO UPDATE SET "
        "password = excluded.password, "
        "is_admin = 1",
        (USERNAME, hashed),
    )
    conn.commit()

print(f"✅ Admin ensured/updated: {USERNAME}")
