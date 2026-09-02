# SCHOLARS HAVEN V3.1 - GLASSMORPHISM UI
from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
import json
import os
import random
import string

app = Flask(__name__, static_folder='static')
app.secret_key = "scholars_haven_secret_2026"

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
else:
    DATABASE_URL = 'sqlite:///quiz.db'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

QUIZ_DURATION = 180 # 3 minutes
ADMIN_PASSWORD = "ScholarsAdmin123"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100))
    has_attempted = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    start_time = db.Column(db.Float, default=0)
    submitted_at = db.Column(db.Float, default=0)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    prompt = db.Column(db.Text)
    options = db.Column(db.Text)
    answer = db.Column(db.String(5))

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    subject = db.Column(db.String(100))
    answers_json = db.Column(db.Text)
    score = db.Column(db.Integer)
    submitted_at = db.Column(db.Float)

ALL_QUESTIONS = { ... } # keep your 9 subjects here, unchanged

def load_questions():
    db.create_all()
    if Question.query.count() == 0:
        for subject, questions in ALL_QUESTIONS.items():
            for q, opts, a in questions:
                db.session.add(Question(subject=subject, prompt=q, options=opts, answer=a))
        db.session.commit()
    return Question.query.count()

def generate_password():
    return "SH" + ''.join(random.choices(string.digits, k=4))

BASE_CSS = """<style> @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap'); body {font-family: 'Poppins', sans-serif; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f4f7fb;}.container {background:white; padding:30px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.15); width:90%; max-width:800px;} h1 {color:#1a3b6d; text-align:center; margin-bottom:10px;}.logo {width:120px; display:block; margin:0 auto 15px;}.user-greet {text-align:center; color:#1a3b6d; font-weight:600; margin-bottom:20px; font-size:18px;} input, select, button {width:100%; padding:14px; margin-top:12px; border-radius:10px; border:1px solid #ccc; font-size:16px; box-sizing:border-box;} button {background:#1a3b6d; color:white; border:none; cursor:pointer; font-weight:600; transition:0.3s;} button:hover {background:#0f274d; transform:translateY(-2px);}.timer {background:#ff4757; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; font-size:18px; margin-bottom:15px;}.question-box {background:#f8f9ff; padding:20px; border-radius:12px; border-left:5px solid #1a3b6d; margin-bottom:20px;}.question-title {font-size:20px; font-weight:600; color:#1a3b6d; margin-bottom:15px;}.options label {display:block; background:white; padding:14px; margin:10px 0; border-radius:10px; border:2px solid #e0e0e0; cursor:pointer; transition:0.2s; font-size:16px;}.options label:hover {border-color:#1a3b6d; background:#f0f4ff;}.options input[type="radio"] {display:none;}.options label:has(input:checked) {border-color:#1a3b6d; background:#e8eeff; font-weight:700;}.progress {height:8px; background:#e0e0e0; border-radius:10px; margin-bottom:20px;}.progress-bar {height:8px; background:#1a3b6d; border-radius:10px; transition:width 0.3s;} table {width:100%; border-collapse: collapse; margin-top:20px; font-size:14px;} th, td {padding:10px; border:1px solid #ddd; text-align:center;} th {background:#1a3b6d; color:white;} a {color:#1a3b6d; text-decoration:none; font-weight:600; margin-right:10px;}.correct {color:green; font-weight:700;}.wrong {color:red; font-weight:700;}.home-body {background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height:100vh;}.home-container {background:rgba(255,255,255,0.15); backdrop-filter:blur(20px); border:1px solid rgba(255,255,255,0.2); border-radius:24px; box-shadow:0 20px 60px rgba(0,0,0,0.3);}.home-container h1,.home-container p {color:white;}.home-container input,.home-container select {background:rgba(255,255,255,0.2); color:white; border:1px solid rgba(255,255,255,0.3);}.home-container input::placeholder {color:rgba(255,255,255,0.7);}.home-container button {background:white; color:#667eea; font-size:18px; font-weight:700;}.home-container a {color:white; text-decoration:underline;}.password-wrapper { display: flex; gap: 8px; align-items: center; }.password-wrapper input { flex: 1; margin: 0; }.icon-btn { padding: 10px 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; background: #e5e7eb; color:#000; width:auto;}.copied { color: #16a34a; font-size: 12px; display: none; }.msg { background: rgba(255,255,255,0.2); padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; color: white; margin: 15px 0; } </style>"""

subject_options = "".join([f"<option>{s}</option>" for s in ALL_QUESTIONS.keys()])

LOGIN_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><img src="{{ url_for('static', filename='raven.png') }}" class="logo" style="width:100px; filter:drop-shadow(0 4px 10px rgba(0,0,0,0.3))"><h1 style="font-size:28px; margin-bottom:8px">Scholars'Haven</h1><p style="text-align:center; color:rgba(255,255,255,0.8); margin-bottom:30px">UTME CBT Portal</p>{% if error %}<p style="background:rgba(255,0,0,0.2); color:white; padding:10px; border-radius:8px; text-align:center">{{error}}</p>{% endif %}<form method="POST"><input name="name" placeholder="👤 Full Name" required><input type="password" name="password" placeholder="🔒 Password" required><button>Login →</button></form><p style="text-align:center; margin-top:20px; color:rgba(255,255,255,0.9)"><a href="/register">New Student?</a> | <a href="/admin">Admin</a></p></div></body>"""

REGISTER_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><h1>📝 Create Account</h1><form method="POST"><input name="name" placeholder="👤 Enter your full name" required>{% if password %}<div class="password-wrapper"><input type="password" id="passwordField" value="{{password}}" readonly><button type="button" class="icon-btn" onclick="togglePassword()" title="Show/Hide">👁️</button><button type="button" class="icon-btn" onclick="copyPassword()" title="Copy">📋</button></div><span id="copiedText" class="copied">Copied!</span><div class="msg">✅ Account Created! Save this password: <b>{{password}}</b></div>{% endif %}<button type="submit">Generate Password</button></form>{% if error %}<div class="msg" style="background:rgba(255,0,0,0.2);">{{error}}</div>{% endif %}<p style="text-align:center; margin-top:15px"><a href="/">Already have account? Login</a></p><script>function togglePassword() {var x = document.getElementById("passwordField"); x.type = x.type === "password"? "text" : "password";} function copyPassword() {var x = document.getElementById("passwordField"); navigator.clipboard.writeText(x.value); document.getElementById("copiedText").style.display = "inline"; setTimeout(() => { document.getElementById("copiedText").style.display = "none"; }, 2000);}</script></div></body>"""

# Keep all your other routes: QUIZ_TEMPLATE, ADMIN_TEMPLATE, etc exactly as they are
# ... paste the rest of your code from /init to /logout here unchanged ...

if __name__ == "__main__": app.run(host="0.0.0.0", port=5000, debug=False)