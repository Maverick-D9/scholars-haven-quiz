# SCHOLARS HAVEN V3.0.0 - REGISTER + PASSWORD SYSTEM
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
    password = db.Column(db.String(20), nullable=False) # <-- NEW
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

ALL_QUESTIONS = {
    "Maths - Ratio, Percentage and Proportion": [
        ("If A:B = 3:5 and B:C = 10:7, find A:C", "a) 3:7\nb) 6:7\nc) 30:35\nd) 5:7", "b"),
        ("What percentage of 80 is 20?", "a) 20%\nb) 25%\nc) 30%\nd) 40%", "b"),
        ("A man shared 9000 in ratio 2:3:4. How much did the second person get?", "a) 2000\nb) 3000\nc) 4000\nd) 5000", "b"),
        ("Increase 250 by 12%", "a) 270\nb) 280\nc) 290\nd) 300", "b"),
        ("If 5 men can build a wall in 8 days, how long will 8 men take?", "a) 3 days\nb) 4 days\nc) 5 days\nd) 6 days", "c"),
        ("The ratio of boys to girls in a class is 4:3. If there are 28 boys, how many girls?", "a) 18\nb) 21\nc) 24\nd) 27", "b"),
        ("A price was reduced from 4000 to 3400. What is the percentage decrease?", "a) 10%\nb) 15%\nc) 20%\nd) 25%", "b"),
        ("Divide 56 in the ratio 3:5", "a) 20, 36\nb) 21, 35\nc) 22, 34\nd) 24, 32", "b"),
        ("If 3/4 of a number is 60, what is the number?", "a) 70\nb) 75\nc) 80\nd) 90", "c"),
        ("What is the simple interest on 50000 for 2 years at 4% per annum?", "a) 2000\nb) 4000\nc) 5000\nd) 8000", "b")
    ],
    #... KEEP ALL YOUR OTHER 8 SUBJECTS HERE...
    "Physics - Dimension, Scalar and Vector": [],
    "Chemistry - Mole, Empirical Formula, Molecular Formula, Vapour Density": [],
    "English - Use of Has, Have and Had": [],
    "Biology - Cell Structure and Functions": [],
    "Economics - Demand and Supply": [],
    "Government - Constitutional Development in Nigeria": [],
    "Literature in English - Drama": [],
    "CRS - The Call of Abraham and Covenant": []
}

def load_questions():
    db.drop_all()
    db.create_all()
    for subject, questions in ALL_QUESTIONS.items():
        for q, opts, a in questions:
            db.session.add(Question(subject=subject, prompt=q, options=opts, answer=a))
    db.session.commit()
    return Question.query.count()

def generate_password():
    return "SH" + ''.join(random.choices(string.digits, k=4))

BASE_CSS = """<style> @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap'); body {font-family: 'Poppins', sans-serif; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f4f7fb;}.container {background:white; padding:30px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.15); width:90%; max-width:800px;} h1 {color:#1a3b6d; text-align:center; margin-bottom:10px;}.logo {width:120px; display:block; margin:0 auto 15px;}.user-greet {text-align:center; color:#1a3b6d; font-weight:600; margin-bottom:20px; font-size:18px;} input, select, button {width:100%; padding:14px; margin-top:12px; border-radius:10px; border:1px solid #ccc; font-size:16px; box-sizing:border-box;} button {background:#1a3b6d; color:white; border:none; cursor:pointer; font-weight:600; transition:0.3s;} button:hover {background:#0f274d; transform:translateY(-2px);}.timer {background:#ff4757; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; font-size:18px; margin-bottom:15px;}.question-box {background:#f8f9ff; padding:20px; border-radius:12px; border-left:5px solid #1a3b6d; margin-bottom:20px;}.question-title {font-size:20px; font-weight:600; color:#1a3b6d; margin-bottom:15px;}.options label {display:block; background:white; padding:14px; margin:10px 0; border-radius:10px; border:2px solid #e0e0e0; cursor:pointer; transition:0.2s; font-size:16px;}.options label:hover {border-color:#1a3b6d; background:#f0f4ff;}.options input[type="radio"] {display:none;}.options label:has(input:checked) {border-color:#1a3b6d; background:#e8eeff; font-weight:700;}.progress {height:8px; background:#e0e0e0; border-radius:10px; margin-bottom:20px;}.progress-bar {height:8px; background:#1a3b6d; border-radius:10px; transition:width 0.3s;} table {width:100%; border-collapse: collapse; margin-top:20px; font-size:14px;} th, td {padding:10px; border:1px solid #ddd; text-align:center;} th {background:#1a3b6d; color:white;} a {color:#1a3b6d; text-decoration:none; font-weight:600; margin-right:10px;}.correct {color:green; font-weight:700;}.wrong {color:red; font-weight:700;}.home-body {background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a3b6d); background-size: 400% 400%; animation: gradient 15s ease infinite;} @keyframes gradient {0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;}}.home-container {background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border:1px solid rgba(255,255,255,0.2);}.home-container h1,.home-container p {color:white;}.home-container input,.home-container select {background:rgba(255,255,255,0.2); color:white; border:1px solid rgba(255,255,255,0.3);}.home-container input::placeholder {color:rgba(255,255,255,0.7);}.home-container button {background:white; color:#1a3b6d;}.home-container a {color:white;}.password-wrapper { display: flex; gap: 8px; align-items: center; }.password-wrapper input { flex: 1; margin: 0; }.icon-btn { padding: 10px 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; background: #e5e7eb; color:#000; width:auto;}.copied { color: #16a34a; font-size: 12px; display: none; }.msg { background: #dcfce7; padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; color: #166534; margin: 15px 0; } </style>"""

subject_options = "".join([f"<option>{s}</option>" for s in ALL_QUESTIONS.keys()])

LOGIN_TEMPLATE = BASE_CSS + f"""<body class="home-body"><div class="container home-container">
<img src="{{{{ url_for('static', filename='raven.png') }}}}" class="logo" alt="Scholars Haven Raven Logo">
<h1>Scholars'Haven Login</h1>{% if error %}<p style="color:yellow; text-align:center">{{{{error}}}}</p>{% endif %}
<form method="POST"><input name="name" placeholder="Enter your full name" required><input type="password" name="password" placeholder="Enter your password" required><button>Login</button></form>
<p style="text-align:center; margin-top:15px"><a href="/register">New Student? Register Here</a> | <a href="/admin">Admin Login</a></p></div></body>"""

REGISTER_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container">
<h1>📝 Create Account</h1>
<form method="POST"><input name="name" placeholder="Enter your full name" required>
{% if password %}
<div class="password-wrapper">
    <input type="password" id="passwordField" value="{{password}}" readonly>
    <button type="button" class="icon-btn" onclick="togglePassword()" title="Show/Hide">👁️</button>
    <button type="button" class="icon-btn" onclick="copyPassword()" title="Copy">📋</button>
</div>
<span id="copiedText" class="copied">Copied!</span>
<div class="msg">✅ Account Created! Save this password: <b>{{password}}</b></div>
{% endif %}
<button type="submit">Generate Password</button></form>
{% if error %}<div class="msg" style="background:#fee2e2; color:#991b1b;">{{error}}</div>{% endif %}
<p style="text-align:center; margin-top:15px"><a href="/">Already have account? Login</a></p>
<script>function togglePassword() {var x = document.getElementById("passwordField"); x.type = x.type === "password"? "text" : "password";} function copyPassword() {var x = document.getElementById("passwordField"); navigator.clipboard.writeText(x.value); document.getElementById("copiedText").style.display = "inline"; setTimeout(() => { document.getElementById("copiedText").style.display = "none"; }, 2000);}</script>
</div></body>"""

QUIZ_TEMPLATE = BASE_CSS + """<div class="container"><h1>Scholars'Haven: {{subject}}</h1><div class="user-greet">Hi {{user_name}} 👋</div><div class="progress"><div class="progress-bar" style="width: {{progress}}%"></div></div><div class="timer">⏱ Time Left: <span id="timer">{{time_left}}</span> seconds</div><form method="POST"><div class="question-box"><div class="question-title">Question {{q_num}} of 10</div><div>{{question.prompt}}</div></div><div class="options">{% for opt in question.options.split('\\n') %}<label><input type="radio" name="answer" value="{{opt[0]}}" required><span>{{opt}}</span></label>{% endfor %}</div><button>Next Question →</button></form><script>let time = {{time_left}};let timer = setInterval(()=>{time--;document.getElementById('timer').innerText = time;if(time <= 0){clearInterval(timer); document.querySelector('form').submit();}}, 1000)</script></div>"""

ADMIN_LOGIN_TEMPLATE = BASE_CSS + """<div class="container"><h1>Admin Login</h1>{% if error %}<p style="color:red; text-align:center">{{error}}</p>{% endif %}<form method="POST"><input type="password" name="password" placeholder="Enter Admin Password" required><button>Login</button></form></div>"""

ADMIN_TEMPLATE = BASE_CSS + """<div class="container"><h1>Admin Panel v3.0.0</h1><p style="color:green; font-weight:700;">✅ PASSWORD LOGIN ACTIVE | 1 ATTEMPT TOTAL</p><a href="/wipe_db" onclick="return confirm('DANGER: This will DELETE ALL USERS AND ATTEMPTS.')" style="background:#ff4757; color:white; padding:12px 20px; border-radius:8px; display:inline-block; margin-bottom:15px; font-weight:700;">🗑️ WIPE ENTIRE DB</a><a href="/logout" style="float:right">Logout</a><table><tr><th>Name</th><th>Password</th><th>Subject Taken</th><th>Score</th><th>Actions</th></tr>{% for u in users %}<tr><td>{{u.name}}</td><td>{{u.password}}</td><td>{{u.subject if u.subject else '-'}}</td><td>{{u.score}}/10</td><td><a href="/reset_user/{{u.id}}" style="color:#ff4757; font-weight:700;">Delete User</a></td></tr>{% endfor %}</table></div>"""

SUBMIT_TEMPLATE = BASE_CSS + """<div class="container"><h1>Submitted ✅</h1><p style="text-align:center; font-size:18px">Thank you {{name}}!<br>You cannot take any other subject again.</p><a href="/">Back to Login</a></div>"""

@app.route("/init")
def init_db():
    with app.app_context(): count = load_questions()
    return BASE_CSS + f"<div class='container'><h1 style='color:green; text-align:center'>Database Initialized ✅</h1><p style='text-align:center; font-size:18px'>Loaded {count} questions. Old users deleted.</p><a href='/' style='background:#1a3b6d; color:white; padding:12px 20px; border-radius:8px;'>Go Home</a></div>"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].lower().strip()
        password = request.form["password"]
        user = User.query.filter_by(name=name, password=password).first()
        if user:
            session["user_id"] = user.id; session["user_name"] = user.name
            return redirect("/home")
        else: return render_template_string(LOGIN_TEMPLATE, error="Invalid Name or Password")
    return render_template_string(LOGIN_TEMPLATE, error=None)

@app.route("/register", methods=["GET", "POST"])
def register():
    password = None; error = None
    if request.method == "POST":
        name = request.form["name"].lower().strip()
        if User.query.filter_by(name=name).first():
            error = "Name already taken. Try another name."
        else:
            password = generate_password()
            new_user = User(name=name, password=password)
            db.session.add(new_user); db.session.commit()
    return render_template_string(REGISTER_TEMPLATE, password=password, error=error)

@app.route("/home")
def home():
    if "user_id" not in session: return redirect("/")
    return render_template_string(BASE_CSS + f"""<body class="home-body"><div class="container home-container">
<h1>Welcome {{session['user_name'].title()}}</h1><p style="text-align:center">UTME CBT | 10 Questions | 3 Minutes | 1 ATTEMPT TOTAL</p>
<form method="POST" action="/start_quiz"><select name="subject" required><option value="" disabled selected>Select Subject</option>{subject_options}</select><button>Start Quiz</button></form>
<p style="text-align:center; margin-top:15px"><a href="/logout">Logout</a></p></div></body>""")

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if user.has_attempted: return BASE_CSS + f"<div class='container'><h1>Already Attempted</h1><p>Hi {user.name.title()}, you have already taken {user.subject}. 1 attempt total only.</p><a href='/logout'>Logout</a></div>"
    subject = request.form["subject"]
    subject_questions = Question.query.filter_by(subject=subject).all()
    ids = [q.id for q in subject_questions]; random.shuffle(ids); session["shuffled_ids"] = ids
    session["q_index"] = 0; session["score"] = 0; session["answers"] = {}; session["subject"] = subject
    user.subject = subject; user.start_time = time.time(); db.session.commit(); return redirect("/quiz")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if time.time() - user.start_time > QUIZ_DURATION: return redirect("/submit")
    time_left = int(QUIZ_DURATION - (time.time() - user.start_time))
    question_ids = session["shuffled_ids"]; questions = [Question.query.get(qid) for qid in question_ids]
    q_index = session["q_index"]
    if q_index >= 10: return redirect("/submit")
    if request.method == "POST":
        ans = request.form["answer"].lower().strip(); session["answers"][str(q_index+1)] = ans
        if ans == questions[q_index].answer: session["score"] += 1
        session["q_index"] += 1; session.modified = True; return redirect("/quiz")
    progress = int((q_index / 10) * 100)
    return render_template_string(QUIZ_TEMPLATE, subject=session["subject"], question=questions[q_index], q_num=q_index+1, time_left=time_left, progress=progress, user_name=session["user_name"])

@app.route("/submit")
def submit():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    user.score = session["score"]; user.has_attempted = True; user.submitted_at = time.time()
    attempt = Attempt(user_id=user.id, subject=session["subject"], answers_json=json.dumps(session["answers"]), score=session["score"], submitted_at=time.time())
    db.session.add(attempt); db.session.commit(); name = user.name.title(); session.clear()
    return render_template_string(SUBMIT_TEMPLATE, name=name)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD: session['is_admin'] = True; return redirect("/admin_panel")
        else: return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Wrong Password")
    return render_template_string(ADMIN_LOGIN_TEMPLATE, error=None)

@app.route("/admin_panel")
def admin_panel():
    if not session.get('is_admin'): return redirect("/admin")
    users = User.query.order_by(User.id.desc()).all()
    return render_template_string(ADMIN_TEMPLATE, users=users)

@app.route("/reset_user/<int:user_id>")
def reset_user(user_id):
    if not session.get('is_admin'): return "Unauthorized"
    user = User.query.get(user_id)
    Attempt.query.filter_by(user_id=user_id).delete()
    db.session.delete(user); db.session.commit(); return redirect("/admin_panel")

@app.route("/wipe_db")
def wipe_db():
    if not session.get('is_admin'): return redirect("/admin")
    db.drop_all(); db.create_all(); return redirect("/admin_panel")

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

if __name__ == "__main__": app.run(host="0.0.0.0", port=5000, debug=False)