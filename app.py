from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# === App setup ===
app = Flask(__name__)
app.secret_key = 'secretkey123'  # Replace with a secure key in production


# === Database connection ===
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# === Home route ===
@app.route('/')
def home():
    conn = get_db_connection()
    comments = conn.execute(
        'SELECT user, content, created_at FROM comments ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('index.html', comments=comments)


# === Register route ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return 'Username already exists.'

        # 🔐 Auto-login after successful registration
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()

        session['username'] = user['username']
        session['is_admin'] = bool(user['is_admin'])

        if user['is_admin']:
            return redirect('/admin')
        return redirect('/')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])  # 🟢 store admin flag

            if user['is_admin']:
                return redirect('/admin')  # optional: admin panel route
            return redirect('/')
        else:
            return 'Invalid credentials. Try again.'

    return render_template('login.html')



# === Logout route ===
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# === Comment route ===
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    topic = request.args.get('topic', 'Unknown Topic')

    if request.method == 'POST':
        if 'username' not in session:
            return redirect('/login')

        content = request.form['content']
        user = session['username']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO comments (user, content, topic) VALUES (?, ?, ?)',
            (user, content, topic)
        )
        conn.commit()
        conn.close()

        return redirect('/comment?topic=' + topic)

    conn = get_db_connection()
    comments = conn.execute(
        'SELECT user, content, created_at FROM comments WHERE topic = ? ORDER BY created_at DESC',
        (topic,)
    ).fetchall()
    conn.close()

    return render_template('comment.html', topic=topic, comments=comments)


# === Static page routes ===
@app.route('/realms')
def realms():
    return render_template('realms.html')


@app.route('/codex')
def codex():
    return render_template('codex.html')


@app.route('/tavern')
def tavern():
    return render_template('tavern.html')


@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return "Access denied. Admins only.", 403

    return render_template('admin_dashboard.html')

@app.route('/admin/users')
def admin_users():
    if not session.get('is_admin'):
        return "Access denied", 403

    conn = get_db_connection()
    users = conn.execute('SELECT id, username, is_admin FROM users').fetchall()
    conn.close()

    return render_template('admin_users.html', users=users)


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('is_admin'):
        return "Access denied", 403

    conn = get_db_connection()
    current_user = conn.execute(
        'SELECT id FROM users WHERE username = ?',
        (session['username'],)
    ).fetchone()

    if current_user and current_user['id'] == user_id:
        conn.close()
        return "You cannot delete yourself.", 400

    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return redirect('/admin/users')


# === App runner ===
if __name__ == '__main__':
    app.run(debug=True)
