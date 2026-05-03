from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets

app = Flask(__name__)
# FIX 02 — 256 bits d'entropie : impossible à deviner ou bruteforcer.
app.secret_key = secrets.token_hex(32)

DATABASE = 'database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email    TEXT,
            bio      TEXT DEFAULT "Pas encore de bio."
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            author     TEXT NOT NULL,
            content    TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    try:
        db.execute(
            'INSERT INTO users (username, password, email, bio) VALUES (?, ?, ?, ?)',
            ('alice', generate_password_hash('password123'),
             'alice@example.com', 'Administratrice du site.')
        )
        db.execute(
            'INSERT INTO users (username, password, email, bio) VALUES (?, ?, ?, ?)',
            ('bob', generate_password_hash('hunter2'),
             'bob@example.com', 'Utilisateur classique.')
        )
    except sqlite3.IntegrityError:
        pass
    db.commit()
    db.close()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        # FIX 01 — Requête paramétrée : le ? empêche toute injection SQL.
        # Le mot de passe est vérifié séparément via check_password_hash.
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Connexion réussie !', 'success')
            return redirect(url_for('profile', user_id=user['id']))
        flash('Identifiants incorrects.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnecté.', 'success')
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email    = request.form.get('email', '')
        db = get_db()
        try:
            db.execute(
                'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password), email)
            )
            db.commit()
            flash('Compte créé, connecte-toi !', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Ce nom d'utilisateur est déjà pris.", 'danger')
        finally:
            db.close()
    return render_template('register.html')


@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session:
        flash('Connecte-toi pour accéder aux profils.', 'danger')
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    if not user:
        flash('Utilisateur introuvable.', 'danger')
        return redirect(url_for('home'))
    return render_template('profile.html', user=user)


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login'))
        content = request.form['content'].strip()
        if content:
            db = get_db()
            db.execute(
                'INSERT INTO comments (user_id, author, content) VALUES (?, ?, ?)',
                (session['user_id'], session['username'], content)
            )
            db.commit()
            db.close()
        return redirect(url_for('comments'))
    db = get_db()
    all_comments = db.execute(
        'SELECT * FROM comments ORDER BY created_at DESC'
    ).fetchall()
    db.close()
    return render_template('comments.html', comments=all_comments)


@app.route('/ping', methods=['GET', 'POST'])
def ping():
    result = None
    if request.method == 'POST':
        result = "[Faille 5 — Command Injection pas encore implémentée]"
    return render_template('ping.html', result=result)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    message = None
    if request.method == 'POST':
        message = "[Faille 6 — Upload non filtré pas encore implémentée]"
    return render_template('upload.html', message=message)


@app.route('/aws')
def aws():
    return render_template('aws.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
