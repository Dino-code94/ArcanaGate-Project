import sqlite3


def has_column(conn, table, col):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


with sqlite3.connect("database.db") as conn:
    # 1) Ensure is_admin column exists
    if not has_column(conn, "users", "is_admin"):
        conn.execute(
            "ALTER TABLE users "
            "ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0"
        )
        conn.commit()
        print("✅ is_admin column added.")
    else:
        print("ℹ️ is_admin column already exists.")

    # 2) Ensure username is unique (safe to run repeatedly)
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username "
        "ON users(username)"
    )
    conn.commit()
    print("✅ UNIQUE index on username ensured.")
