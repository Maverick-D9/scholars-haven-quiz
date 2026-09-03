# SCHOLARS HAVEN V3.3.1 - 1 ATTEMPT TOTAL + FULL DARK GOLD RIPPLE
from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from questions import ALL_QUESTIONS
import time
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

QUIZ_DURATION = 180
ADMIN_PASSWORD = "ScholarsAdmin123"
QUESTIONS_PER_QUIZ = 10

SUBJECT_COLORS = {
    "Mathematics": "0,212,255", "English": "255,215,0", "Physics": "255,71,87",
    "Chemistry": "46,213,115", "Biology": "112,161,255", "Government": "255,165,2",
    "Economics": "123,237,159", "Literature": "232,67,147", "CRS": "162,155,254"
}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100))
    has_attempted = db.Column(db.Boolean, default=False) # <-- 1 ATTEMPT TOTAL FLAG
    score = db.Column(db.Integer, default=0)
    start_time = db.Column(db.Float, default=0)
    submitted_at = db.Column(db.Float, default=0)
    music_on = db.Column(db.Boolean, default=False, nullable=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    prompt = db.Column(db.Text)
    options = db.Column(db.Text)
    answer = db.Column(db.String(5))

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

def get_base_css(r="255",g="215",b="0"):
    color_rgb = f"{r},{g},{b}"
    return f"""<style> 
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap'); 
body {{font-family: 'Poppins', sans-serif; margin:0; padding:20px; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#0a0a0a; color:#e5e5e5;}}
.container {{background:linear-gradient(145deg, #1a1a1a, #0f0f0f); padding:30px; border-radius:24px; width:90%; max-width:1000px; border: 1px solid rgba({color_rgb},0.2); position:relative; overflow: hidden; box-shadow: 0 0 40px rgba({color_rgb},0.15);}}
.container::before {{content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px; border-radius: 26px; background: linear-gradient(90deg, transparent 0%, rgba({color_rgb},0.1) 20%, rgba({color_rgb},1) 50%, rgba({color_rgb},0.1) 80%, transparent 100%); background-size: 400% 100%; animation: borderRipple 5s linear infinite; z-index: -1; filter: blur(4px);}}
@keyframes borderRipple {{0% {{ background-position: 0% 50%; }} 100% {{ background-position: 400% 50%; }}}}
h1 {{color:rgb({color_rgb}); text-align:center; text-shadow:0 0 20px rgba({color_rgb},0.8); margin-bottom:10px;}}
.user-greet {{text-align:center; color:rgb({color_rgb}); font-weight:600; margin-bottom:20px; font-size:18px;}}
.input-group {{position:relative; margin-top:12px;}}
.input-group input {{width:100%; padding:14px 14px 14px 45px; border-radius:10px; border:1px solid rgb({color_rgb}); background:#1a1a1a; color:rgb({color_rgb}); font-size:16px; box-sizing:border-box;}}
.input-icon {{position:absolute; left:15px; top:50%; transform:translateY(-50%); font-size:18px;}}
select, button {{width:100%; padding:14px; margin-top:12px; border-radius:10px; border:1px solid rgb({color_rgb}); background:#1a1a1a; color:rgb({color_rgb}); font-size:16px; box-sizing:border-box;}}
button {{background:linear-gradient(135deg, rgb({color_rgb}), #ffb700); color:#000; font-weight:700; cursor:pointer; transition:0.3s;}}
button:hover {{transform:translateY(-3px); box-shadow:0 10px 30px rgba({color_rgb},0.8);}}
.btn-red {{background:linear-gradient(135deg, #ff4757, #ff2e43); color:white;}}
.btn-green {{background:linear-gradient(135deg, #2ed573, #1e90ff); color:white;}}
.timer {{background:#ff4757; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; font-size:18px; margin-bottom:15px;}}
.question-box {{background:#222; padding:20px; border-radius:12px; border-left:5px solid rgb({color_rgb}); margin-bottom:20px;}}
.logo {{width:120px; display:block; margin:0 auto 15px; filter:drop-shadow(0 0 25px rgba({color_rgb},1))}}
@keyframes pulse {{0%{{box-shadow:0 0 0 0 rgba({color_rgb},0.8)}} 70%{{box-shadow:0 0 0 25px rgba({color_rgb},0)}} 100%{{box-shadow:0 0 0 0 rgba({color_rgb},0)}}}}
table {{width:100%; border-collapse:collapse; margin-top:20px;}}
th, td {{padding:12px; border:1px solid #333; text-align:left;}}
th {{background:rgba({color_rgb},0.1); color:rgb({color_rgb});}}
.actions {{display:flex; gap:8px;}}
.actions button {{padding:8px 12px; font-size:14px; margin:0; width:auto;}}
.warning {{background:rgba(255,71,87,0.2); color:#ff4757; padding:15px; border-radius:10px; text-align:center; border:1px solid #ff4757;}}
</style>"""

subject_options = "".join([f"<option>{s}</option>" for s in ALL_QUESTIONS])

def render_page(template, color_rgb="255,215,0", **kwargs):
    r,g,b = color_rgb.split(",")
    return render_template_string(get_base_css(r,g,b) + template, **kwargs)

LOGIN_TEMPLATE = """<body><div class="container"><img src="{{ url_for('static', filename='raven.png') }}" class="logo"><h1>Scholars'Haven</h1><p style="text-align:center; color:rgba(255,215,0,0.8); margin-bottom:30px;">UTME CBT Portal</p>{% if error %}<p class="warning">{{error}}</p>{% endif %}<form method="POST"><div class="input-group"><span class="input-icon">👤</span><input name="name" placeholder="Full Name" required></div><div class="input-group"><span class="input-icon">🔒</span><input type="password" name="password" placeholder="Password" required></div><button>Login →</button></form><a href="/admin" style="display:block; text-align:center; margin-top:20px; color:rgba(255,215,0,0.6);">Admin Panel</a></div></body>"""

HOME_TEMPLATE = """<body><audio id="bgMusic" loop><source src="{{ url_for('static', filename='lofi.mp3') }}" type="audio/mpeg"></audio><div class="container"><h1>Welcome {{user_name}}</h1><div class="user-greet">UTME CBT | 10 Questions | 3 Minutes | 1 Attempt Only</div><button id="musicBtn" onclick="toggleMusic()" style="width:auto; margin:0 auto 20px; display:block; animation:pulse 2s infinite">🔊 Music: ON</button><form method="POST" action="/start_quiz"><select name="subject" required><option value="">-- Select Subject --</option>{{subject_options|safe}}</select><button>Start Quiz</button></form><script>const audio=document.getElementById('bgMusic');let musicOn=true;function toggleMusic(){musicOn=!musicOn;if(musicOn){audio.play()}else{audio.pause()}document.getElementById('musicBtn').innerText=musicOn?'🔊 Music: ON':'🔇 Music: OFF'}document.addEventListener('click',()=>{if(musicOn)audio.play()},{once:true});</script></div></body>"""

QUIZ_TEMPLATE = """<body><div class="container"><h1>{{subject}}</h1><div class="user-greet">Hi {{user_name}} 👋</div><div class="timer">⏱ Time Left: <span id="timer">{{time_left}}</span> seconds</div><form method="POST"><div class="question-box"><div style="font-size:20px; font-weight:600; color:rgb({{color_rgb}}); margin-bottom:15px;">Question {{q_num}} of {{total_q}}</div><div>{{question.prompt}}</div></div><div>{% for opt in question.options.split('\\n') %}<label style="display:flex; align-items:center; gap:12px; background:#1a1a1a; padding:14px; margin:10px 0; border-radius:10px; border:2px solid #333; cursor:pointer;"><input type="radio" name="answer" value="{{opt[0]}}" required style="accent-color: rgb({{color_rgb}}); width:20px; height:20px;"><span>{{opt}}</span></label>{% endfor %}</div><button>Next Question →</button></form><script>let time={{time_left}};setInterval(()=>{time--;document.getElementById('timer').innerText=time;if(time<=0)document.querySelector('form').submit()},1000)</script></div></body>"""

SUBMIT_TEMPLATE = """<body><div class="container"><h1>Submitted ✅</h1><p style="text-align:center; font-size:18px">Thank you {{name}}!<br>Score: {{score}}/{{total_q}} in {{subject}}</p><p style="text-align:center; color:rgba(255,71,87,0.8)">You cannot attempt again</p></div></body>"""

@app.route("/init")
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        count = load_questions()
    return f"Database RESET. Loaded {count} questions. <a href='/'>Go Home</a>"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].lower().strip()
        password = request.form["password"]
        user = User.query.filter_by(name=name, password=password).first()
        if user:
            session["user_id"] = user.id; session["user_name"] = user.name
            return redirect("/home")
        else: return render_page(LOGIN_TEMPLATE, error="Invalid Name or Password")
    return render_page(LOGIN_TEMPLATE, error=None)

@app.route("/home")
def home():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if user.has_attempted:
        return render_page('<body><div class="container"><h1>Attempt Completed</h1><p class="warning">You have already completed your 1 attempt.</p></div></body>')
    user_name = session['user_name'].title()
    return render_page(HOME_TEMPLATE, user_name=user_name, subject_options=subject_options)

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if user.has_attempted: return "Already Attempted"
    
    subject = request.form["subject"]
    session["subject"] = subject
    subject_questions = Question.query.filter_by(subject=subject).all()

    if len(subject_questions) == 0: return "No questions for this subject"

    ids = [q.id for q in subject_questions]; random.shuffle(ids)
    total_q = min(len(ids), QUESTIONS_PER_QUIZ)
    session["shuffled_ids"] = ids[:total_q]
    session["q_index"] = 0; session["score"] = 0; session["answers"] = {}; session["total_q"] = total_q
    user.subject = subject; user.start_time = time.time(); db.session.commit()
    color_rgb = SUBJECT_COLORS.get(subject, "255,215,0")
    return redirect(f"/quiz?color={color_rgb}")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session: return redirect("/")
    if "shuffled_ids" not in session: return redirect("/home")
    
    user = User.query.get(session["user_id"])
    if time.time() - user.start_time > QUIZ_DURATION: return redirect("/submit")
    time_left = int(QUIZ_DURATION - (time.time() - user.start_time))
    
    question_ids = session["shuffled_ids"]
    questions = [Question.query.get(qid) for qid in question_ids if Question.query.get(qid)]
    q_index = session["q_index"]
    total_q = session.get("total_q", len(questions))
    
    if q_index >= total_q: return redirect("/submit")
    
    if request.method == "POST":
        ans = request.form["answer"].lower().strip()
        session["answers"][str(q_index+1)] = ans
        if ans == questions[q_index].answer: session["score"] += 1
        session["q_index"] += 1
        session.modified = True
        color_rgb = request.args.get('color', '255,215,0')
        return redirect(f"/quiz?color={color_rgb}")
    
    color_rgb = request.args.get('color', '255,215,0')
    return render_page(QUIZ_TEMPLATE, color_rgb=color_rgb, subject=session["subject"], question=questions[q_index], q_num=q_index+1, total_q=total_q, time_left=time_left, user_name=session["user_name"].title())

@app.route("/submit")
def submit():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if not user.has_attempted:
        user.has_attempted = True
        user.score = session.get("score", 0)
        db.session.commit()
    return render_page(SUBMIT_TEMPLATE, name=session["user_name"].title(), score=user.score, total_q=session.get("total_q", 10), subject=user.subject)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect("/admin")
        else: return render_page('<body><div class="container"><h1>Wrong Password</h1><a href="/admin">Try Again</a></div></body>')
    
    if not session.get("is_admin"):
        return render_page('<body><div class="container"><h1>Admin Login</h1><form method=POST><div class="input-group"><span class="input-icon">🔑</span><input type=password name=password placeholder="Admin Password"></div><button>Login</button></form></div></body>')
    
    users = User.query.order_by(User.id.desc()).all()
    rows = ""
    for u in users:
        status = "✅ Attempted" if u.has_attempted else "⏳ Pending"
        rows += f"""<tr>
        <td>{u.name.title()}</td>
        <td>{u.password}</td>
        <td>{u.subject or '-'}</td>
        <td>{u.score}</td>
        <td>{status}</td>
        <td class="actions">
            <form method="POST" action="/admin/reset/{u.id}"><button class="btn-green">🔄 Reset</button></form>
            <form method="POST" action="/admin/delete/{u.id}" onsubmit="return confirm('Delete {u.name}?')"><button class="btn-red">🗑️ Delete</button></form>
        </td>
        </tr>"""
    
    new_pass = generate_password()
    admin_html = f"""<body><div class="container"><h1>Admin Dashboard 👑</h1>
    <form method="POST" action="/admin/create"><h3>➕ Create New User</h3>
    <div class="input-group"><span class="input-icon">👤</span><input name="name" placeholder="Student Full Name" required></div>
    <div class="input-group"><span class="input-icon">🔑</span><input name="password" value="{new_pass}" readonly></div>
    <button class="btn-green">Generate & Create User</button></form>
    <h3 style="margin-top:30px;">All Users</h3>
    <table><tr><th>Name</th><th>Password</th><th>Subject</th><th>Score</th><th>Status</th><th>Actions</th></tr>{rows}</table>
    <br><a href="/" style="display:block; text-align:center; color:gold;">Back to Home</a>
    </div></body>"""
    return render_page(admin_html)

@app.route("/admin/create", methods=["POST"])
def create_user():
    if not session.get("is_admin"): return redirect("/admin")
    name = request.form["name"].lower().strip()
    password = request.form["password"]
    if User.query.filter_by(name=name).first(): return "User already exists <a href='/admin'>Back</a>"
    user = User(name=name, password=password)
    db.session.add(user); db.session.commit()
    return redirect("/admin")

@app.route("/admin/reset/<int:user_id>", methods=["POST"])
def reset_user(user_id):
    if not session.get("is_admin"): return redirect("/admin")
    user = User.query.get(user_id)
    user.has_attempted = False; user.score = 0; user.subject = None
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/delete/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    if not session.get("is_admin"): return redirect("/admin")
    user = User.query.get(user_id)
    db.session.delete(user); db.session.commit()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)