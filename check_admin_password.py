import sqlite3
from werkzeug.security import check_password_hash

# --- SETTINGS (diagnostic only) ---
USERNAME = "admin"                
PLAINTEXT = "securepassword123"   

try:
    # Connect and return rows as tuples (fine for one-column select)
    with sqlite3.connect("database.db") as conn:
        # Parameterized query (safer than f-strings)
        row = conn.execute(
            "SELECT password "
            "FROM users "
            "WHERE username = ?",
            (USERNAME,),
        ).fetchone()

    if row is None:
        print("User not found")
    else:
        stored_hash = row[0]
        is_ok = check_password_hash(stored_hash, PLAINTEXT)
        print("✅ Password correct" if is_ok else "❌ Wrong password")

except sqlite3.Error as e:
    # Helpful if the DB file is missing/corrupt
    print(f"DB error: {e}")
