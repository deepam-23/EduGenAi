# app.py
import os
import json
import sqlite3
from datetime import datetime
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, send_file, g)
from werkzeug.security import generate_password_hash, check_password_hash
from quiz import QuizGenerator
from dotenv import load_dotenv

load_dotenv()
DATABASE = 'data.db'
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "supersecretkey")
quiz_gen = QuizGenerator()

# ---------- DB helpers ----------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        need_init = not os.path.exists(DATABASE)
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        if need_init:
            init_db(db)
    return db

def init_db(db):
    cur = db.cursor()
    cur.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    cur.execute('''
    CREATE TABLE history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score INTEGER,
        total INTEGER,
        quiz_json TEXT,
        taken_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        if not email or not password:
            flash("Please fill all fields.", "error")
            return redirect(url_for('signup'))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for('signup'))
        db = get_db()
        try:
            db.execute('INSERT INTO users (email, password) VALUES (?,?)',
                       (email, generate_password_hash(password)))
            db.commit()
            flash("Signup successful. Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Email already registered. Please login.", "error")
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()
        if not email or not password:
            flash("Please provide email and password.", "error")
            return redirect(url_for('login'))
        user = query_db('SELECT * FROM users WHERE email=?', (email,), one=True)
        if not user:
            flash("Email not found. Please sign up.", "error")
            return redirect(url_for('signup'))
        if not check_password_hash(user['password'], password):
            flash("Incorrect password. Try again.", "error")
            return redirect(url_for('login'))
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        flash("Login successful.", "success")
        return redirect(url_for('generate_quiz'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for('home'))

# ---------- Generate quiz page ----------
@app.route('/generate', methods=['GET','POST'])
def generate_quiz():
    if 'user_id' not in session:
        flash("Please login.", "error")
        return redirect(url_for('login'))
    if request.method == 'POST':
        topic = request.form.get('topic','').strip()
        num = int(request.form.get('num_questions') or 5)
        pdf_file = request.files.get('pdf')
        quiz = quiz_gen.generate_quiz(pdf_file=pdf_file, topic=topic or "General", num_questions=num)
        session['current_quiz'] = json.dumps(quiz)
        return redirect(url_for('view_quiz'))
    return render_template('generate_quiz.html')

# ---------- Preview quiz ----------
@app.route('/view_quiz')
def view_quiz():
    if 'user_id' not in session:
        flash("Please login.", "error")
        return redirect(url_for('login'))
    raw = session.get('current_quiz')
    if not raw:
        flash("No generated quiz found. Create one.", "error")
        return redirect(url_for('generate_quiz'))
    quiz = json.loads(raw)
    return render_template('view_quiz.html', quiz=quiz)

# ---------- Download quiz ----------
@app.route('/download_quiz')
def download_quiz():
    raw = session.get('current_quiz')
    if not raw:
        flash("No quiz to download", "error")
        return redirect(url_for('generate_quiz'))
    quiz = json.loads(raw)
    include_answers = request.args.get('with_answers','0') == '1'
    filename = quiz_gen.export_pdf(quiz, include_answers=include_answers, title="Generated Quiz")
    return send_file(filename, as_attachment=True)

# ---------- Take quiz ----------
@app.route('/take_quiz', methods=['GET','POST'])
def take_quiz():
    if 'user_id' not in session:
        flash("Please login.", "error")
        return redirect(url_for('login'))
    raw = session.get('current_quiz')
    if not raw:
        flash("No quiz available. Generate one first.", "error")
        return redirect(url_for('generate_quiz'))
    quiz = json.loads(raw)
    if request.method == 'POST':
        score = 0
        answers = {}
        for i, q in enumerate(quiz):
            key = f"q{i}"
            val = request.form.get(key)
            answers[key] = val
            if val == q.get('answer'):
                score += 1
        db = get_db()
        db.execute('INSERT INTO history (user_id, score, total, quiz_json, taken_at) VALUES (?,?,?,?,?)',
                   (session['user_id'], score, len(quiz), json.dumps(quiz), datetime.utcnow().isoformat()))
        db.commit()
        session['last_result'] = json.dumps({"score": score, "total": len(quiz)})
        return redirect(url_for('quiz_result'))
    return render_template('take_quiz.html', quiz=quiz)

# ---------- Result ----------
@app.route('/quiz_result')
def quiz_result():
    raw = session.get('last_result')
    if not raw:
        flash("No recent quiz result.", "error")
        return redirect(url_for('dashboard'))
    data = json.loads(raw)
    return render_template('quiz_result.html', result=data)

# ---------- History ----------
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("Please login.", "error")
        return redirect(url_for('login'))
    rows = query_db('SELECT * FROM history WHERE user_id=? ORDER BY taken_at DESC', (session['user_id'],))
    history = []
    for r in rows:
        history.append({
            "id": r['id'],
            "score": r['score'],
            "total": r['total'],
            "taken_at": r['taken_at'],
            "quiz": json.loads(r['quiz_json']) if r['quiz_json'] else []
        })
    return render_template('history.html', history=history)

# ---------- Dashboard ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please login.", "error")
        return redirect(url_for('login'))
    rows = query_db('SELECT COUNT(*) as cnt FROM history WHERE user_id=?', (session['user_id'],), one=True)
    attempts = rows['cnt'] if rows else 0
    return render_template('dashboard.html', attempts=attempts)

if __name__ == "__main__":
    app.run(debug=True)
