# SCHOLARS HAVEN V2.15.6 - FLASK 3 FIX
from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
import json
import os
import random

app = Flask(__name__)
app.secret_key = "scholars_haven_secret_2026"

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
else:
    DATABASE_URL = 'sqlite:///quiz.db'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

QUIZ_DURATION = 180
ADMIN_PASSWORD = "ScholarsAdmin123"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    subject = db.Column(db.String(50))
    has_attempted = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    start_time = db.Column(db.Float, default=0)
    submitted_at = db.Column(db.Float, default=0)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50))
    prompt = db.Column(db.Text)
    options = db.Column(db.Text)
    answer = db.Column(db.String(1))

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(50))
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
    "Physics - Dimension, Scalar and Vector": [
        ("Which of the following is a scalar quantity?", "a) Force\nb) Velocity\nc) Mass\nd) Displacement", "c"),
        ("The dimension of force is", "a) MLT^-1\nb) MLT^-2\nc) ML^2T^-2\nd) ML^-1T^-2", "b"),
        ("Which of these is a vector quantity?", "a) Energy\nb) Power\nc) Momentum\nd) Temperature", "c"),
        ("The dimension of pressure is", "a) ML^-1T^-2\nb) MLT^-2\nc) ML^2T^-2\nd) ML^-2T^-2", "a"),
        ("Speed and velocity differ because", "a) Speed is scalar, velocity is vector\nb) Speed is vector, velocity is scalar\nc) Both are scalars\nd) Both are vectors", "a"),
        ("Which of the following has the same dimension as energy?", "a) Force\nb) Power\nc) Work\nd) Momentum", "c"),
        ("The dimension of acceleration is", "a) LT^-1\nb) LT^-2\nc) L^2T^-2\nd) L^-1T^2", "b"),
        ("Which of the following pairs are both vectors?", "a) Mass and Weight\nb) Force and Acceleration\nc) Work and Energy\nd) Distance and Speed", "b"),
        ("The dimension of frequency is", "a) T^-1\nb) T\nc) LT^-1\nd) L^-1T", "a"),
        ("A quantity that has magnitude but no direction is called a ___", "a) Vector\nb) Scalar\nc) Tensor\nd) Matrix", "b")
    ],
    "Chemistry - Mole, Empirical Formula, Molecular Formula, Vapour Density": [
        ("What is the number of moles in 44g of CO2? [C=12, O=16]", "a) 0.5\nb) 1.0\nc) 1.5\nd) 2.0", "b"),
        ("The empirical formula of a compound with 40% C, 6.7% H, 53.3% O is", "a) CH2O\nb) C2H4O2\nc) C6H12O6\nd) CHO", "a"),
        ("Vapour density is defined as", "a) Mass of gas / Mass of hydrogen\nb) Density of gas / Density of hydrogen\nc) Molar mass / 2\nd) 2 x Molar mass", "c"),
        ("How many molecules are in 1 mole of a substance?", "a) 6.02 x 10^22\nb) 6.02 x 10^23\nc) 3.01 x 10^23\nd) 1.00 x 10^24", "b"),
        ("The molecular formula of a compound with empirical formula CH2O and molar mass 180 is", "a) CH2O\nb) C2H4O2\nc) C3H6O3\nd) C6H12O6", "d"),
        ("If the vapour density of a gas is 22, what is its molar mass?", "a) 11\nb) 22\nc) 44\nd) 88", "c"),
        ("What is the empirical formula of C6H12O6?", "a) C6H12O6\nb) C3H6O3\nc) C2H4O2\nd) CH2O", "d"),
        ("1 mole of any gas at STP occupies", "a) 11.2 dm^3\nb) 22.4 dm^3\nc) 44.8 dm^3\nd) 24.0 dm^3", "b"),
        ("The mass of 0.5 moles of NaCl is [Na=23, Cl=35.5]", "a) 29.25g\nb) 58.5g\nc) 117g\nd) 23g", "a"),
        ("A gas has vapour density 16. Its molecular mass is", "a) 8\nb) 16\nc) 32\nd) 64", "c")
    ],
    "English - Use of Has, Have and Had": [
        ("She ___ finished her assignment before I arrived.", "a) has\nb) have\nc) had\nd) having", "c"),
        ("They ___ three cars.", "a) has\nb) have\nc) had\nd) having", "b"),
        ("He ___ a meeting yesterday.", "a) has\nb) have\nc) had\nd) having", "c"),
        ("The students ___ submitted their forms.", "a) has\nb) have\nc) had\nd) having", "b"),
        ("By next year, I ___ graduated.", "a) has\nb) have\nc) will have\nd) had", "c"),
        ("My father ___ been a teacher for 20 years.", "a) has\nb) have\nc) had\nd) having", "a"),
        ("We ___ not seen him since Monday.", "a) has\nb) have\nc) had\nd) having", "b"),
        ("She said she ___ lost her keys.", "a) has\nb) have\nc) had\nd) having", "c"),
        ("___ you ever been to Abuja?", "a) Has\nb) Have\nc) Had\nd) Having", "b"),
        ("The baby ___ been crying all night.", "a) has\nb) have\nc) had\nd) having", "a")
    ]
}

def load_questions():
    with app.app_context():
        db.create_all()
        db.session.query(Question).delete()
        db.session.commit()
        for subject, questions in ALL_QUESTIONS.items():
            for q, opts, a in questions:
                db.session.add(Question(subject=subject, prompt=q, options=opts, answer=a))
        db.session.commit()
        return Question.query.count()

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
body {font-family: 'Poppins', sans-serif; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f4f7fb;}
.container {background:white; padding:30px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.15); width:90%; max-width:800px;}
h1 {color:#1a3b6d; text-align:center; margin-bottom:10px;}
.user-greet {text-align:center; color:#1a3b6d; font-weight:600; margin-bottom:20px; font-size:18px;}
input, select, button {width:100%; padding:14px; margin-top:12px; border-radius:10px; border:1px solid #ccc; font-size:16px;}
button {background:#1a3b6d; color:white; border:none; cursor:pointer; font-weight:600; transition:0.3s;}
button:hover {background:#0f274d; transform:translateY(-2px);}
.timer {background:#ff4757; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; font-size:18px; margin-bottom:15px;}
.question-box {background:#f8f9ff; padding:20px; border-radius:12px; border-left:5px solid #1a3b6d; margin-bottom:20px;}
.question-title {font-size:20px; font-weight:600; color:#1a3b6d; margin-bottom:15px;}
.options label {display:block; background:white; padding:14px; margin:10px 0; border-radius:10px; border:2px solid #e0e0e0; cursor:pointer; transition:0.2s; font-size:16px;}
.options label:hover {border-color:#1a3b6d; background:#f0f4ff;}
.options input[type="radio"] {display:none;}
.options label:has(input:checked) {border-color:#1a3b6d; background:#e8eeff; font-weight:700;}
.progress {height:8px; background:#e0e0e0; border-radius:10px; margin-bottom:20px;}
.progress-bar {height:8px; background:#1a3b6d; border-radius:10px; transition:width 0.3s;}
table {width:100%; border-collapse: collapse; margin-top:20px; font-size:14px;}
th, td {padding:10px; border:1px solid #ddd; text-align:center;}
th {background:#1a3b6d; color:white;}
a {color:#1a3b6d; text-decoration:none; font-weight:600; margin-right:10px;}
.correct {color:green; font-weight:700;}
.wrong {color:red; font-weight:700;}
.home-body {background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #1a3b6d); background-size: 400% 400%; animation: gradient 15s ease infinite;}
@keyframes gradient {0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;}}
.home-container {background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border:1px solid rgba(255,255,255,0.2);}
.home-container h1,.home-container p {color:white;}
.home-container input,.home-container select {background:rgba(255,255,255,0.2); color:white; border:1px solid rgba(255,255,255,0.3);}
.home-container input::placeholder {color:rgba(255,255,255,0.7);}
.home-container button {background:white; color:#1a3b6d;}
.home-container a {color:white;}
</style>
"""

HOME_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container"><h1>Scholars'Haven Quiz Space</h1><p style="text-align:center">UTME CBT | 10 Questions | 3 Minutes | 1 ATTEMPT TOTAL</p><form method="POST"><input name="name" placeholder="Enter your full name" required><select name="subject" required><option value="" disabled selected>Select Subject</option><option>Maths - Ratio, Percentage and Proportion</option><option>Physics - Dimension, Scalar and Vector</option><option>Chemistry - Mole, Empirical Formula, Molecular Formula, Vapour Density</option><option>English - Use of Has, Have and Had</option></select><button>Start Quiz</button></form><p style="text-align:center; margin-top:15px"><a href="/admin">Admin Login</a> | <a href="/init" style="color:yellow; font-weight:700;">CLICK TO INIT DB</a></p></div></body>"""

QUIZ_TEMPLATE = BASE_CSS + """<div class="container"><h1>Scholars'Haven: {{subject}}</h1><div class="user-greet">Hi {{user_name}} 👋</div><div class="progress"><div class="progress-bar" style="width: {{progress}}%"></div></div><div class="timer">⏱ Time Left: <span id="timer">{{time_left}}</span> seconds</div><form method="POST"><div class="question-box"><div class="question-title">Question {{q_num}} of 10</div><div>{{question.prompt}}</div></div><div class="options">{% for opt in question.options.split('\\n') %}<label><input type="radio" name="answer" value="{{opt[0]}}" required><span>{{opt}}</span></label>{% endfor %}</div><button>Next Question →</button></form><script>let time = {{time_left}};let timer = setInterval(()=>{time--;document.getElementById('timer').innerText = time;if(time <= 0){clearInterval(timer); document.querySelector('form').submit();}}, 1000)</script></div>"""

ADMIN_LOGIN_TEMPLATE = BASE_CSS + """<div class="container"><h1>Admin Login</h1>{% if error %}<p style="color:red; text-align:center">{{error}}</p>{% endif %}<form method="POST"><input type="password" name="password" placeholder="Enter Admin Password" required><button>Login</button></form></div>"""

ADMIN_TEMPLATE = BASE_CSS + """<div class="container"><h1>Admin Panel v2.15.6</h1><p style="color:green; font-weight:700;">✅ 1 ATTEMPT TOTAL ENFORCED</p><p>All records are saved permanently.</p><a href="/wipe_db" onclick="return confirm('DANGER: This will DELETE ALL USERS AND ATTEMPTS. Cannot be undone.')" style="background:#ff4757; color:white; padding:12px 20px; border-radius:8px; display:inline-block; margin-bottom:15px; font-weight:700;">🗑️ WIPE ENTIRE DB</a><a href="/logout" style="float:right">Logout</a><table><tr><th>Name</th><th>First Subject</th><th>Score</th><th>Time Submitted</th><th>Actions</th></tr>{% for a in attempts %}<tr><td>{{a.user_name}}</td><td>{{a.subject}}</td><td>{{a.score}}/10</td><td>{{a.sub_time}}</td><td><a href="/review/{{a.id}}">Review</a> <a href="/reset/{{a.id}}" style="color:#ff4757; font-weight:700;">Reset</a></td></tr>{% endfor %}</table></div>"""

REVIEW_TEMPLATE = BASE_CSS + """<div class="container"><h1>Review: {{user_name}} - {{subject}}</h1><p>Score: {{score}}/10</p><a href="/admin_panel">← Back to Admin</a>{% for q in review_data %}<div class="question-box"><div class="question-title">Q{{q.num}}: {{q.prompt}}</div><p><b>Correct Answer:</b> <span class="correct">{{q.correct}}</span></p><p><b>Student Answer:</b> <span class="{{'correct' if q.is_correct else 'wrong'}}">{{q.student}}</span></p></div>{% endfor %}</div>"""

SUBMIT_TEMPLATE = BASE_CSS + """<div class="container"><h1>Submitted ✅</h1><p style="text-align:center; font-size:18px">Thank you {{name}}!<br>You cannot take any other subject again.</p></div>"""

@app.route("/init") # MANUAL INIT FOR FLASK 3
def init_db():
    count = load_questions()
    return f"<h1 style='text-align:center'>Database Initialized</h1><p style='text-align:center'>Loaded {count} questions. <a href='/'>Go Home</a></p>"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"].strip()
        subject = request.form["subject"]
        user = User.query.filter_by(name=name).first()
        if user and user.has_attempted: return BASE_CSS + f"<div class='container'><h1>Already Attempted A Quiz</h1><p>Hi {name}, you have already taken {user.subject}. 1 attempt total only. Contact admin to reset.</p></div>"
        if not user: user = User(name=name, subject=subject); db.session.add(user); db.session.commit()
        subject_questions = Question.query.filter_by(subject=subject).all()
        if len(subject_questions) == 0: return BASE_CSS + "<div class='container'><h1>Error</h1><p>No questions found. Click 'CLICK TO INIT DB' on home page first</p></div>"
        ids = [q.id for q in subject_questions]; random.shuffle(ids); session["shuffled_ids"] = ids
        session["user_id"] = user.id; session["user_name"] = user.name; session["q_index"] = 0; session["score"] = 0; session["answers"] = {}; session["subject"] = subject
        user.start_time = time.time(); db.session.commit(); return redirect("/quiz")
    return render_template_string(HOME_TEMPLATE)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if time.time() - user.start_time > QUIZ_DURATION: return redirect("/submit")
    time_left = int(QUIZ_DURATION - (time.time() - user.start_time))
    question_ids = session["shuffled_ids"]; questions = [Question.query.get(qid) for qid in question_ids]
    q_index = session["q_index"]
    if q_index >= len(questions): return redirect("/submit")
    if request.method == "POST":
        ans = request.form["answer"].lower().strip(); session["answers"][str(q_index+1)] = ans
        if ans == questions[q_index].answer: session["score"] += 1
        session["q_index"] += 1; session.modified = True; return redirect("/quiz")
    progress = int((q_index / len(questions)) * 100)
    return render_template_string(QUIZ_TEMPLATE, subject=session["subject"], question=questions[q_index], q_num=q_index+1, time_left=time_left, progress=progress, user_name=session["user_name"])

@app.route("/submit")
def submit():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    user.score = session["score"]; user.has_attempted = True; user.submitted_at = time.time()
    attempt = Attempt(user_id=user.id, subject=session["subject"], answers_json=json.dumps(session["answers"]), score=session["score"], submitted_at=time.time())
    db.session.add(attempt); db.session.commit(); session.pop("shuffled_ids", None)
    return render_template_string(SUBMIT_TEMPLATE, name=user.name, subject=session["subject"])

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session['is_admin'] = True; return redirect("/admin_panel")
        else: return render_template_string(ADMIN_LOGIN_TEMPLATE, error="Wrong Password")
    return render_template_string(ADMIN_LOGIN_TEMPLATE, error=None)

@app.route("/admin_panel")
def admin_panel():
    if not session.get('is_admin'): return redirect("/admin")
    attempts = Attempt.query.all(); clean_attempts = []
    for a in attempts:
        user = User.query.get(a.user_id)
        if user:
            a.user_name = user.name; a.sub_time = datetime.fromtimestamp(a.submitted_at).strftime('%d-%b %H:%M'); clean_attempts.append(a)
    return render_template_string(ADMIN_TEMPLATE, attempts=clean_attempts)

@app.route("/review/<int:attempt_id>")
def review(attempt_id):
    if not session.get('is_admin'): return redirect("/admin")
    attempt = Attempt.query.get(attempt_id); user = User.query.get(attempt.user_id)
    questions = Question.query.filter_by(subject=attempt.subject).all(); answers = json.loads(attempt.answers_json); review_data = []
    for i, q in enumerate(questions[:10]):
        q_num = str(i+1); review_data.append({"num": q_num, "prompt": q.prompt, "correct": q.answer.upper(), "student": answers.get(q_num, "No Answer").upper(), "is_correct": answers.get(q_num) == q.answer})
    return render_template_string(REVIEW_TEMPLATE, user_name=user.name, subject=attempt.subject, score=attempt.score, review_data=review_data)

@app.route("/reset/<int:attempt_id>")
def reset(attempt_id):
    if not session.get('is_admin'): return "Unauthorized"
    attempt = Attempt.query.get(attempt_id); user = User.query.get(attempt.user_id)
    db.session.delete(attempt); db.session.delete(user); db.session.commit(); return redirect("/admin_panel")

@app.route("/wipe_db")
def wipe_db():
    if not session.get('is_admin'): return redirect("/admin")
    db.session.query(Attempt).delete(); db.session.query(User).delete(); db.session.commit(); return redirect("/admin_panel")

@app.route("/logout")
def logout(): session.pop('is_admin', None); return redirect("/")

if __name__ == "__main__": app.run(host="0.0.0.0", port=5000, debug=False)