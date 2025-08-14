import sqlite3
from werkzeug.security import generate_password_hash

USERS = [
    ("dino", "jesusofsuburbia", 1),        # admin
    ("admin", "securepassword123", 1),     # admin
]


def upsert_users(conn):
    # make username unique (safe to run many times)
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username "
        "ON users(username)"
    )
    for u, pw, is_admin in USERS:
        conn.execute(
            "INSERT INTO users (username, password, is_admin) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(username) DO UPDATE SET "
            "password = excluded.password, "
            "is_admin = excluded.is_admin",
            (u, generate_password_hash(pw), is_admin),
        )


if __name__ == "__main__":
    with sqlite3.connect("database.db") as conn:
        upsert_users(conn)
        conn.commit()
    print("✅ Ensured users:", ", ".join(u for u, _, _ in USERS))
