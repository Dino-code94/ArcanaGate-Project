from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secretkey123'  # Replace with a secure key in production

# Connect to SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def home():
    conn = get_db_connection()
    comments = conn.execute(
        'SELECT user, content, created_at FROM comments ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    return render_template('index.html', comments=comments)


@app.route('/register', methods=['GET', 'POST'])
def register():
    print("📥 Register route hit")  # Debug print
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
        conn.close()
        return redirect('/login')

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
            return redirect('/')
        else:
            return 'Invalid credentials. Try again.'

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/comment', methods=['POST'])
def comment():
    if 'username' not in session:
        return redirect('/login')

    content = request.form['content']
    user = session['username']

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO comments (user, content) VALUES (?, ?)',
        (user, content)
    )
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/realms')
def realms():
    return render_template('realms.html')


if __name__ == '__main__':
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)
