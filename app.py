# SCHOLARS HAVEN V3.2.1 - DARK GOLD GLITTER UI FULL
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
    "Physics - Dimension, Scalar and Vector": [("Which of the following is a scalar quantity?", "a) Force\nb) Velocity\nc) Mass\nd) Displacement", "c"),("The dimension of force is", "a) MLT^-1\nb) MLT^-2\nc) ML^2T^-2\nd) ML^-1T^-2", "b"),("Which of these is a vector quantity?", "a) Energy\nb) Power\nc) Momentum\nd) Temperature", "c"),("The dimension of pressure is", "a) ML^-1T^-2\nb) MLT^-2\nc) ML^2T^-2\nd) ML^-2T^-2", "a"),("Speed and velocity differ because", "a) Speed is scalar, velocity is vector\nb) Speed is vector, velocity is scalar\nc) Both are scalars\nd) Both are vectors", "a"),("Which of the following has the same dimension as energy?", "a) Force\nb) Power\nc) Work\nd) Momentum", "c"),("The dimension of acceleration is", "a) LT^-1\nb) LT^-2\nc) L^2T^-2\nd) L^-1T^2", "b"),("Which of the following pairs are both vectors?", "a) Mass and Weight\nb) Force and Acceleration\nc) Work and Energy\nd) Distance and Speed", "b"),("The dimension of frequency is", "a) T^-1\nb) T\nc) LT^-1\nd) L^-1T", "a"),("A quantity that has magnitude but no direction is called a ___", "a) Vector\nb) Scalar\nc) Tensor\nd) Matrix", "b")],
    "Chemistry - Mole, Empirical Formula, Molecular Formula, Vapour Density": [("What is the number of moles in 44g of CO2? [C=12, O=16]", "a) 0.5\nb) 1.0\nc) 1.5\nd) 2.0", "b"),("The empirical formula of a compound with 40% C, 6.7% H, 53.3% O is", "a) CH2O\nb) C2H4O2\nc) C6H12O6\nd) CHO", "a"),("Vapour density is defined as", "a) Mass of gas / Mass of hydrogen\nb) Density of gas / Density of hydrogen\nc) Molar mass / 2\nd) 2 x Molar mass", "c"),("How many molecules are in 1 mole of a substance?", "a) 6.02 x 10^22\nb) 6.02 x 10^23\nc) 3.01 x 10^23\nd) 1.00 x 10^24", "b"),("The molecular formula of a compound with empirical formula CH2O and molar mass 180 is", "a) CH2O\nb) C2H4O2\nc) C3H6O3\nd) C6H12O6", "d"),("If the vapour density of a gas is 22, what is its molar mass?", "a) 11\nb) 22\nc) 44\nd) 88", "c"),("What is the empirical formula of C6H12O6?", "a) C6H12O6\nb) C3H6O3\nc) C2H4O2\nd) CH2O", "d"),("1 mole of any gas at STP occupies", "a) 11.2 dm^3\nb) 22.4 dm^3\nc) 44.8 dm^3\nd) 24.0 dm^3", "b"),("The mass of 0.5 moles of NaCl is [Na=23, Cl=35.5]", "a) 29.25g\nb) 58.5g\nc) 117g\nd) 23g", "a"),("A gas has vapour density 16. Its molecular mass is", "a) 8\nb) 16\nc) 32\nd) 64", "c")],
    "English - Use of Has, Have and Had": [("She ___ finished her assignment before I arrived.", "a) has\nb) have\nc) had\nd) having", "c"),("They ___ three cars.", "a) has\nb) have\nc) had\nd) having", "b"),("He ___ a meeting yesterday.", "a) has\nb) have\nc) had\nd) having", "c"),("The students ___ submitted their forms.", "a) has\nb) have\nc) had\nd) having", "b"),("By next year, I ___ graduated.", "a) has\nb) have\nc) will have\nd) had", "c"),("My father ___ been a teacher for 20 years.", "a) has\nb) have\nc) had\nd) having", "a"),("We ___ not seen him since Monday.", "a) has\nb) have\nc) had\nd) having", "b"),("She said she ___ lost her keys.", "a) has\nb) have\nc) had\nd) having", "c"),("___ you ever been to Abuja?", "a) Has\nb) Have\nc) Had\nd) Having", "b"),("The baby ___ been crying all night.", "a) has\nb) have\nc) had\nd) having", "a")],
    "Biology - Cell Structure and Functions": [("The organelle responsible for protein synthesis is", "a) Mitochondrion\nb) Ribosome\nc) Chloroplast\nd) Nucleus", "b"),("Plant cells differ from animal cells because they have", "a) Nucleus\nb) Cell membrane\nc) Cell wall\nd) Cytoplasm", "c"),("The powerhouse of the cell is", "a) Ribosome\nb) Mitochondrion\nc) Lysosome\nd) Golgi body", "b"),("Which organelle contains chlorophyll?", "a) Mitochondrion\nb) Ribosome\nc) Chloroplast\nd) Vacuole", "c"),("DNA is found in the", "a) Cytoplasm\nb) Nucleus\nc) Cell wall\nd) Vacuole", "b"),("The fluid part of the cell is called", "a) Protoplasm\nb) Cytoplasm\nc) Nucleoplasm\nd) Plasma", "b"),("Diffusion is the movement of molecules from", "a) Low to high concentration\nb) High to low concentration\nc) Equal concentration\nd) Nowhere", "b"),("The cell membrane is", "a) Impermeable\nb) Semi-permeable\nc) Fully permeable\nd) Non-permeable", "b"),("Osmosis is the movement of", "a) Water\nb) Salt\nc) Oxygen\nd) Carbon dioxide", "a"),("The function of vacuole in plant cell is", "a) Protein synthesis\nb) Storage\nc) Respiration\nd) Photosynthesis", "b")],
    "Economics - Demand and Supply": [("The law of demand states that price and quantity demanded are", "a) Directly related\nb) Inversely related\nc) Not related\nd) Equal", "b"),("A shift in demand curve to the right is caused by", "a) Increase in price\nb) Increase in income\nc) Decrease in income\nd) Decrease in population", "b"),("Elasticity of demand measures", "a) Price change\nb) Responsiveness of demand to price\nc) Supply change\nd) Income", "b"),("If price increases and total revenue decreases, demand is", "a) Inelastic\nb) Elastic\nc) Unit elastic\nd) Perfectly elastic", "b"),("Substitute goods are goods that", "a) Are used together\nb) Can replace each other\nc) Are inferior\nd) Are luxury", "b"),("Complementary goods are goods that", "a) Replace each other\nb) Are used together\nc) Are normal\nd) Are inferior", "b"),("The supply curve slopes", "a) Downward\nb) Upward\nc) Horizontal\nd) Vertical", "b"),("A decrease in supply causes", "a) Price to fall\nb) Price to rise\nc) Quantity to rise\nd) No change", "b"),("Equilibrium price is where", "a) Demand = Supply\nb) Price is highest\nc) Price is lowest\nd) Supply > Demand", "a"),("Normal goods are goods whose demand", "a) Falls as income rises\nb) Rises as income rises\nc) Is constant\nd) Is zero", "b")],
    "Government - Constitutional Development in Nigeria": [("The first constitution of Nigeria was", "a) 1960 Constitution\nb) 1963 Constitution\nc) 1922 Clifford Constitution\nd) 1999 Constitution", "c"),("The 1963 constitution made Nigeria a", "a) Colony\nb) Republic\nc) Protectorate\nd) Monarchy", "b"),("The Richard Constitution was introduced in", "a) 1946\nb) 1951\nc) 1954\nd) 1960", "a"),("Federalism in Nigeria was introduced by", "a) 1960 Constitution\nb) 1954 Lyttleton Constitution\nc) 1963 Constitution\nd) 1979 Constitution", "b"),("The 1999 constitution is currently in use in Nigeria", "a) True\nb) False\nc) Not sure\nd) None", "a"),("The arm of government that makes laws is", "a) Executive\nb) Legislature\nc) Judiciary\nd) Civil Service", "b"),("The highest court in Nigeria is", "a) High Court\nb) Court of Appeal\nc) Supreme Court\nd) Sharia Court", "c"),("The 1960 constitution was a", "a) Republican constitution\nb) Independence constitution\nc) Military constitution\nd) Draft constitution", "b"),("One feature of parliamentary system is", "a) Separation of powers\nb) Fusion of powers\nc) No prime minister\nd) Military rule", "b"),("The process of amending the constitution is called", "a) Ratification\nb) Amendment\nc) Review\nd) Revision", "b")],
    "Literature in English - Drama": [("A play performed without spoken words is", "a) Tragedy\nb) Comedy\nc) Mime\nd) Farce", "c"),("The main character in a play is called", "a) Protagonist\nb) Antagonist\nc) Villain\nd) Heroine", "a"),("A play with sad ending is", "a) Comedy\nb) Tragedy\nc) Romance\nd) Satire", "b"),("The person who writes a play is called", "a) Actor\nb) Director\nc) Playwright\nd) Producer", "c"),("Dialogue in drama means", "a) Song\nb) Conversation between characters\nc) Narration\nd) Dance", "b"),("The climax of a play is the", "a) Beginning\nb) Highest point of tension\nc) End\nd) Introduction", "b"),("A play for radio is called", "a) Teleplay\nb) Radio drama\nc) Screenplay\nd) Stage play", "b"),("Soliloquy is when a character speaks", "a) To another character\nb) To the audience alone\nc) In a song\nd) In a dance", "b"),("The setting of a play refers to", "a) Characters\nb) Time and place\nc) Plot\nd) Theme", "b"),("Comedy aims to", "a) Make people sad\nb) Make people laugh\nc) Teach morals only\nd) Scare people", "b")],
    "CRS - The Call of Abraham and Covenant": [("Abraham was originally called", "a) Isaac\nb) Jacob\nc) Abram\nd) Lot", "c"),("God promised Abraham that his descendants would be as numerous as", "a) Sand of the sea\nb) Stars of heaven\nc) Both a and b\nd) None", "c"),("The covenant God made with Abraham was sealed with", "a) Baptism\nb) Circumcision\nc) Sacrifice\nd) Prayer", "b"),("Abraham's wife was", "a) Rebecca\nb) Rachel\nc) Sarah\nd) Leah", "c"),("Abraham was called from", "a) Egypt\nb) Canaan\nc) Ur of Chaldeans\nd) Babylon", "c"),("The son of promise to Abraham was", "a) Ishmael\nb) Isaac\nc) Esau\nd) Jacob", "b"),("God tested Abraham by asking him to sacrifice", "a) Isaac\nb) Ishmael\nc) Lot\nd) Jacob", "a"),("Abraham is regarded as the father of", "a) Jews only\nb) Christians only\nc) Faith\nd) Kings", "c"),("The land God promised Abraham was", "a) Egypt\nb) Canaan\nc) Babylon\nd) Assyria", "b"),("Abraham lived to be", "a) 100 years\nb) 120 years\nc) 150 years\nd) 175 years", "d")]
}

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

BASE_CSS = """<style> @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap'); body {font-family: 'Poppins', sans-serif; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f4f7fb;}.container {background:white; padding:30px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.15); width:90%; max-width:800px;} h1 {color:#1a3b6d; text-align:center; margin-bottom:10px;}.logo {width:120px; display:block; margin:0 auto 15px;}.user-greet {text-align:center; color:#1a3b6d; font-weight:600; margin-bottom:20px; font-size:18px;} input, select, button {width:100%; padding:14px; margin-top:12px; border-radius:10px; border:1px solid #ccc; font-size:16px; box-sizing:border-box;} button {background:#1a3b6d; color:white; border:none; cursor:pointer; font-weight:600; transition:0.3s;} button:hover {background:#0f274d; transform:translateY(-2px);}.timer {background:#ff4757; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; font-size:18px; margin-bottom:15px;}.question-box {background:#f8f9ff; padding:20px; border-radius:12px; border-left:5px solid #1a3b6d; margin-bottom:20px;}.question-title {font-size:20px; font-weight:600; color:#1a3b6d; margin-bottom:15px;}.options label {display:block; background:white; padding:14px; margin:10px 0; border-radius:10px; border:2px solid #e0e0e0; cursor:pointer; transition:0.2s; font-size:16px;}.options label:hover {border-color:#1a3b6d; background:#f0f4ff;}.options input[type="radio"] {display:none;}.options label:has(input:checked) {border-color:#1a3b6d; background:#e8eeff; font-weight:700;}.progress {height:8px; background:#e0e0e0; border-radius:10px; margin-bottom:20px;}.progress-bar {height:8px; background:#1a3b6d; border-radius:10px; transition:width 0.3s;} table {width:100%; border-collapse: collapse; margin-top:20px; font-size:14px;} th, td {padding:10px; border:1px solid #ddd; text-align:center;} th {background:#1a3b6d; color:white;} a {color:#1a3b6d; text-decoration:none; font-weight:600; margin-right:10px;}.correct {color:green; font-weight:700;}.wrong {color:red; font-weight:700;}

/* DARK SHINY GOLD THEME */
.home-body {background:#0a0a0a; min-height:100vh; position:relative; overflow:hidden;}
.home-body::before {content:''; position:absolute; top:0; left:0; width:100%; height:100%; background:radial-gradient(2px 2px at 20px 30px, #ffd700, transparent), radial-gradient(2px 2px at 40px 70px, #fff, transparent), radial-gradient(2px 2px at 50px 160px, #ffd700, transparent), radial-gradient(2px 2px at 120px 40px, #fff, transparent), radial-gradient(3px 3px at 130px 80px, #ffd700, transparent), radial-gradient(2px 2px at 160px 120px, #fff, transparent); background-size:200px 200px; animation:twinkle 3s linear infinite; z-index:0;}
@keyframes twinkle {0% {opacity:0.3;} 50% {opacity:1;} 100% {opacity:0.3;}}

.home-container {background:linear-gradient(145deg, #1a1a1a, #0f0f0f); border:2px solid #ffd700; border-radius:24px; box-shadow:0 0 30px rgba(255,215,0,0.4), inset 0 0 20px rgba(255,215,0,0.1); position:relative; z-index:1;}
.home-container h1 {color:#ffd700; text-shadow:0 0 10px rgba(255,215,0,0.8);}
.home-container p {color:#e5e5e5;}
.home-container input,.home-container select {background:#1a1a1a; color:#ffd700; border:1px solid #ffd700;}
.home-container input::placeholder {color:rgba(255,215,0,0.5);}
.home-container button {background:linear-gradient(135deg, #ffd700, #ffb700); color:#000; font-size:18px; font-weight:700; box-shadow:0 4px 15px rgba(255,215,0,0.4);}
.home-container button:hover {background:linear-gradient(135deg, #fff, #ffd700); transform:translateY(-2px); box-shadow:0 6px 20px rgba(255,215,0,0.6);}
.home-container a {color:#ffd700; text-decoration:underline;}
.password-wrapper { display: flex; gap: 8px; align-items: center; }.password-wrapper input { flex: 1; margin: 0; }.icon-btn { padding: 10px 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; background: #ffd700; color:#000; width:auto;}.copied { color: #ffd700; font-size: 12px; display: none; }.msg { background: rgba(255,215,0,0.2); padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; color: #ffd700; margin: 15px 0; border:1px solid #ffd700;}

/* Dark Gold Table */
.dark-table th {background:#ffd700; color:#000; font-weight:700;}
.dark-table tr {background:#1a1a1a;}
.dark-table td {color:#e5e5e5; border-color:#333;}
</style>"""

subject_options = "".join([f"<option>{s}</option>" for s in ALL_QUESTIONS])

LOGIN_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><img src="{{ url_for('static', filename='raven.png') }}" class="logo" style="width:100px; filter:drop-shadow(0 0 15px rgba(255,215,0,0.8))"><h1 style="font-size:28px; margin-bottom:8px">Scholars'Haven</h1><p style="text-align:center; color:rgba(255,215,0,0.8); margin-bottom:30px; font-weight:600">UTME CBT Portal | Excellence Through Knowledge</p>{% if error %}<p style="background:rgba(255,0,0,0.2); color:#ffd700; padding:10px; border-radius:8px; text-align:center; border:1px solid #ffd700">{{error}}</p>{% endif %}<form method="POST"><input name="name" placeholder="👤 Full Name" required><input type="password" name="password" placeholder="🔒 Password" required><button>Login →</button></form><p style="text-align:center; margin-top:20px"><a href="/register">New Student?</a> | <a href="/admin">Admin</a></p></div></body>"""

REGISTER_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><h1>📝 Create Account</h1><form method="POST"><input name="name" placeholder="👤 Enter your full name" required>{% if password %}<div class="password-wrapper"><input type="password" id="passwordField" value="{{password}}" readonly><button type="button" class="icon-btn" onclick="togglePassword()" title="Show/Hide">👁️</button><button type="button" class="icon-btn" onclick="copyPassword()" title="Copy">📋</button></div><span id="copiedText" class="copied">Copied!</span><div class="msg">✅ Account Created! Save this password: <b>{{password}}</b></div>{% endif %}<button type="submit">Generate Password</button></form>{% if error %}<div class="msg" style="background:rgba(255,0,0,0.2);">{{error}}</div>{% endif %}<p style="text-align:center; margin-top:15px"><a href="/">Already have account? Login</a></p><script>function togglePassword() {var x = document.getElementById("passwordField"); x.type = x.type === "password"? "text" : "password";} function copyPassword() {var x = document.getElementById("passwordField"); navigator.clipboard.writeText(x.value); document.getElementById("copiedText").style.display = "inline"; setTimeout(() => { document.getElementById("copiedText").style.display = "none"; }, 2000);}</script></div></body>"""

QUIZ_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container"><h1>Scholars'Haven: {{subject}}</h1><div class="user-greet" style="color:#ffd700">Hi {{user_name}} 👋</div><div class="progress"><div class="progress-bar" style="background:#ffd700; width: {{progress}}%"></div></div><div class="timer" style="background:#ffd700; color:#000">⏱ Time Left: <span id="timer">{{time_left}}</span> seconds</div><form method="POST"><div class="question-box" style="background:#1a1a1a; border-left:5px solid #ffd700"><div class="question-title" style="color:#ffd700">Question {{q_num}} of 10</div><div style="color:#e5e5e5">{{question.prompt}}</div></div><div class="options">{% for opt in question.options.split('\\n') %}<label style="background:#1a1a1a; color:#e5e5e5; border:2px solid #333"><input type="radio" name="answer" value="{{opt[0]}}" required><span>{{opt}}</span></label>{% endfor %}</div><button>Next Question →</button></form><script>let time = {{time_left}};let timer = setInterval(()=>{time--;document.getElementById('timer').innerText = time;if(time <= 0){clearInterval(timer); document.querySelector('form').submit();}}, 1000)</script></div></body>"""

ADMIN_LOGIN_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><h1 style="color:#ffd700">🔐 Admin Login</h1>{% if error %}<p style="background:rgba(255,0,0,0.2); color:#ffd700; padding:10px; border-radius:8px; text-align:center; border:1px solid #ffd700">{{error}}</p>{% endif %}<form method="POST"><input type="password" name="password" placeholder="Enter Admin Password" required><button>Login</button></form></div></body>"""

ADMIN_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container" style="max-width:1000px"><h1>👑 Admin Panel v3.2.1</h1><p style="color:#ffd700; font-weight:700; text-align:center">✅ DARK GOLD GLITTER UI ACTIVE | PASSWORD LOGIN | 1 ATTEMPT TOTAL</p><div style="display:flex; justify-content:space-between; margin-bottom:15px; flex-wrap:wrap; gap:10px"><a href="/wipe_db" onclick="return confirm('DANGER: This will DELETE ALL USERS AND ATTEMPTS.')" style="background:#ff4757; color:white; padding:12px 20px; border-radius:8px; font-weight:700; text-decoration:none">🗑️ WIPE ENTIRE DB</a><a href="/logout" style="background:#ffd700; color:#000; padding:12px 20px; border-radius:8px; font-weight:700; text-decoration:none">Logout</a></div><div style="overflow-x:auto"><table class="dark-table"><tr><th>Name</th><th>Password</th><th>Subject Taken</th><th>Score</th><th>Actions</th></tr>{% for u in users %}<tr><td>{{u.name.title()}}</td><td style="color:#ffd700; font-weight:700">{{u.password}}</td><td>{{u.subject if u.subject else '-'}}</td><td style="color:#ffd700; font-weight:700">{{u.score}}/10</td><td><a href="/reset_user/{{u.id}}" style="color:#ff4757; font-weight:700;">Delete</a></td></tr>{% endfor %}</table></div></div></body>"""

SUBMIT_TEMPLATE = BASE_CSS + """<body class="home-body"><div class="container home-container"><h1>Submitted ✅</h1><p style="text-align:center; font-size:18px; color:#e5e5e5">Thank you {{name}}!<br>You cannot take any other subject again.</p><a href="/" style="display:block; text-align:center; margin-top:20px; background:#ffd700; color:#000; padding:12px; border-radius:8px; font-weight:700">Back to Login</a></div></body>"""

@app.route("/init")
def init_db():
    with app.app_context():
        db.session.execute(db.text('DROP TABLE IF EXISTS "attempt" CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS "question" CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS "user" CASCADE'))
        db.session.commit()
        db.create_all()
        count = load_questions()
    return BASE_CSS + f"<body class='home-body'><div class='container home-container'><h1 style='color:#ffd700; text-align:center'>Database RESET ✅</h1><p style='text-align:center; font-size:18px; color:#ffd700'>Loaded {count} questions across 9 subjects. All old users deleted.</p><a href='/' style='background:#ffd700; color:#000; padding:12px 20px; border-radius:8px; font-weight:700; display:block; text-align:center'>Go Home</a></div></body>"

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
    user_name = session['user_name'].title()
    html = BASE_CSS + f"""<body class="home-body"><div class="container home-container"><h1>Welcome {user_name}</h1><p style="text-align:center; color:#ffd700; font-weight:600">UTME CBT | 10 Questions | 3 Minutes | 1 ATTEMPT TOTAL</p><form method="POST" action="/start_quiz"><select name="subject" required><option value="" disabled selected>Select Subject</option>{subject_options}</select><button>Start Quiz</button></form><p style="text-align:center; margin-top:15px"><a href="/logout">Logout</a></p></div></body>"""
    return render_template_string(html)

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if user.has_attempted: return BASE_CSS + f"<body class='home-body'><div class='container home-container'><h1 style='color:#ffd700'>Already Attempted</h1><p style='color:#e5e5e5'>Hi {user.name.title()}, you have already taken {user.subject}. 1 attempt total only.</p><a href='/logout'>Logout</a></div></body>"
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
    time_left = int(QUIZ_DURATION - (time.time() - user.start_time))@app.route("/quiz", methods=["GET", "POST"])
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
    return render_template_string(QUIZ_TEMPLATE, subject=session["subject"], question=questions[q_index], q_num=q_index+1, time_left=time_left, progress=progress, user_name=session["user_name"].title())

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
    db.session.execute(db.text('DROP TABLE IF EXISTS "attempt" CASCADE'))
    db.session.execute(db.text('DROP TABLE IF EXISTS "question" CASCADE'))
    db.session.execute(db.text('DROP TABLE IF EXISTS "user" CASCADE'))
    db.session.commit()
    db.create_all()
    return redirect("/admin_panel")

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

if __name__ == "__main__": app.run(host="0.0.0.0", port=5000, debug=False)