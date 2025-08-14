from flask import (
    Flask, render_template, request, redirect, url_for, session, flash
)
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = Flask(__name__)
app.secret_key = "secretkey123"  # TODO: use a strong secret in production

# enable template auto-reload
app.jinja_env.auto_reload = True
app.config["TEMPLATES_AUTO_RELOAD"] = True

# ---------- DB helpers ----------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


# ---------- Auth helpers ----------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("username"):
            flash("Please log in.", "error")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("Admin access required.", "error")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper


# ---------- Routes ----------
@app.route("/")
def home():
    # figure out admin status from the DB each time
    username = session.get("username")
    is_admin = False

    # one connection to fetch both: admin flag and comments
    conn = get_db_connection()

    if username:
        row = conn.execute(
            "SELECT is_admin FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row:
            is_admin = bool(row["is_admin"])
            # keep session in sync in case it was missing
            session["is_admin"] = is_admin

    comments = conn.execute(
        "SELECT user, content, created_at "
        "FROM comments "
        "ORDER BY created_at DESC"
    ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        comments=comments,
        is_admin=is_admin,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        pw_raw = request.form["password"]

        if not username or not pw_raw:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        pw_hash = generate_password_hash(pw_raw)

        conn = get_db_connection()
        try:
            # is_admin should default to 0 in the schema
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, pw_hash),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            flash("Username already exists.", "error")
            return render_template("register.html")

        user = conn.execute(
            "SELECT username, is_admin "
            "FROM users "
            "WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        session["username"] = user["username"]
        session["is_admin"] = bool(user["is_admin"])

        if session["is_admin"]:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()
        pw_raw = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT id, username, password, is_admin "
            "FROM users "
            "WHERE username = ?",
            (username,),
        ).fetchone()
        conn.close()

        if not user or not check_password_hash(user["password"], pw_raw):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["username"] = user["username"]
        session["is_admin"] = bool(user["is_admin"])

        if session["is_admin"]:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("home"))


@app.route("/comment", methods=["GET", "POST"])
def comment():
    topic = request.args.get("topic", "Unknown Topic")

    if request.method == "POST":
        if "username" not in session:
            return redirect(url_for("login"))

        content = request.form["content"].strip()
        if not content:
            flash("Comment cannot be empty.", "error")
            return redirect(url_for("comment", topic=topic))

        user = session["username"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO comments (user, content, topic) VALUES (?, ?, ?)",
            (user, content, topic),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("comment", topic=topic))

    conn = get_db_connection()
    comments = conn.execute(
        "SELECT user, content, created_at "
        "FROM comments "
        "WHERE topic = ? "
        "ORDER BY created_at DESC",
        (topic,),
    ).fetchall()
    conn.close()

    return render_template("comment.html", topic=topic, comments=comments)


@app.route("/realms")
def realms():
    return render_template("realms.html")


@app.route("/codex")
def codex():
    return render_template("codex.html")


@app.route("/tavern")
def tavern():
    return render_template("tavern.html")


# ---------- Admin ----------
@app.route("/admin")
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/admin/users")
@admin_required
def admin_users():
    conn = get_db_connection()
    users = conn.execute(
        "SELECT id, username, is_admin FROM users"
    ).fetchall()
    conn.close()
    return render_template("admin_users.html", users=users)


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id: int):
    conn = get_db_connection()

    current = conn.execute(
        "SELECT id FROM users WHERE username = ?",
        (session["username"],),
    ).fetchone()

    if current and current["id"] == user_id:
        conn.close()
        return "You cannot delete yourself.", 400

    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_users"))

if __name__ == "__main__":
    app.run(debug=True)
