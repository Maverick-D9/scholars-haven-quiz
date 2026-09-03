# SCHOLARS HAVEN V3.2.7L - 10 Q EACH FROM UTME SYLLABUS + CRASH FIX
from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
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
    has_attempted = db.Column(db.Boolean, default=False)
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

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    subject = db.Column(db.String(100))
    answers_json = db.Column(db.Text)
    score = db.Column(db.Integer)
    submitted_at = db.Column(db.Float)

ALL_QUESTIONS = {
    "Mathematics": [ # Topic 1: Number and Numeration
        ("Convert 1011_2 to base 10", "A. 9\nB. 10\nC. 11\nD. 12", "c"),
        ("If 2x + 5 = 15, find x", "A. 4\nB. 5\nC. 6\nD. 10", "b"),
        ("Find the LCM of 12 and 18", "A. 24\nB. 36\nC. 48\nD. 72", "b"),
        ("Express 0.00045 in standard form", "A. 4.5 x 10^-3\nB. 4.5 x 10^-4\nC. 4.5 x 10^-5\nD. 45 x 10^-4", "b"),
        ("What is 15% of 200?", "A. 20\nB. 25\nC. 30\nD. 35", "c"),
        ("If a : b = 3 : 5 and b = 20, find a", "A. 8\nB. 10\nC. 12\nD. 15", "c"),
        ("Simplify: 2/3 + 1/6", "A. 1/2\nB. 3/9\nC. 5/6\nD. 2/9", "c"),
        ("Find the simple interest on N5000 for 2 years at 4%", "A. N200\nB. N400\nC. N500\nD. N800", "b"),
        ("What is the square root of 169?", "A. 12\nB. 13\nC. 14\nD. 15", "b"),
        ("If x = 3, evaluate x^2 + 2x - 5", "A. 5\nB. 8\nC. 10\nD. 15", "c")
    ],
    "English": [ # Topic 1: Lexis and Structure
        ("Choose the word nearest in meaning: 'Diligent'", "A. Lazy\nB. Hardworking\nC. Careless\nD. Weak", "b"),
        ("Antonym of 'Generous'", "A. Kind\nB. Stingy\nC. Rich\nD. Poor", "b"),
        ("Select the correct spelling", "A. Embarass\nB. Embarrass\nC. Embarras\nD. Embbarass", "b"),
        ("'She sings ___ than her sister'", "A. good\nB. better\nC. best\nD. well", "b"),
        ("The plural of 'Analysis'", "A. Analysiss\nB. Analyses\nC. Analysises\nD. Analysi", "b"),
        ("Choose the correct tense: 'I ___ to Lagos yesterday'", "A. go\nB. goes\nC. went\nD. gone", "c"),
        ("'Neither John nor Mary ___ present'", "A. are\nB. were\nC. is\nD. be", "c"),
        ("Identify the figure of speech: 'A deafening silence'", "A. Simile\nB. Oxymoron\nC. Metaphor\nD. Irony", "b"),
        ("What type of sentence is: 'If you study, you will pass'", "A. Simple\nB. Compound\nC. Complex\nD. Compound-Complex", "c"),
        ("Synonym of 'Vast'", "A. Small\nB. Tiny\nC. Huge\nD. Narrow", "c")
    ],
    "Physics": [ # Topic 1: Interaction of Matter, Space and Time
        ("SI unit of length", "A. Meter\nB. Centimeter\nC. Kilometer\nD. Millimeter", "a"),
        ("Instrument used to measure mass", "A. Spring balance\nB. Beam balance\nC. Meter rule\nD. Thermometer", "b"),
        ("1 hour = ___ seconds", "A. 3600\nB. 1800\nC. 7200\nD. 60", "a"),
        ("Which is a scalar quantity?", "A. Force\nB. Velocity\nC. Speed\nD. Acceleration", "c"),
        ("The area under velocity-time graph gives", "A. Acceleration\nB. Force\nC. Distance\nD. Speed", "c"),
        ("Dimension of force", "A. MLT^-1\nB. MLT^-2\nC. ML^2T^-2\nD. ML^-1T^-2", "b"),
        ("Error due to faulty instrument is called", "A. Random error\nB. Systematic error\nC. Human error\nD. Zero error", "b"),
        ("1 light year is a unit of", "A. Time\nB. Mass\nC. Distance\nD. Speed", "c"),
        ("The S.I unit of time", "A. Minute\nB. Hour\nC. Second\nD. Day", "c"),
        ("Which is not a fundamental quantity?", "A. Length\nB. Mass\nC. Area\nD. Temperature", "c")
    ],
    "Chemistry": [ # Topic 1: Separation Techniques
        ("Method used to separate salt from water", "A. Filtration\nB. Evaporation\nC. Distillation\nD. Chromatography", "b"),
        ("Which mixture can be separated by magnetism?", "A. Sand and salt\nB. Iron and sulfur\nC. Oil and water\nD. Alcohol and water", "b"),
        ("Process of separating components of ink", "A. Crystallization\nB. Sublimation\nC. Chromatography\nD. Decantation", "c"),
        ("Separating petrol from crude oil uses", "A. Fractional distillation\nB. Simple distillation\nC. Filtration\nD. Sieving", "a"),
        ("Which is a chemical method of separation?", "A. Sieving\nB. Magnetism\nC. Precipitation\nD. Decantation", "c"),
        ("Separating immiscible liquids uses", "A. Funnel\nB. Separating funnel\nC. Filter paper\nD. Sieve", "b"),
        ("Sublimation is used for", "A. Salt and water\nB. Iodine and sand\nC. Oil and water\nD. Sugar and sand", "b"),
        ("Purest form of water is obtained by", "A. Boiling\nB. Filtration\nC. Distillation\nD. Chlorination", "c"),
        ("Which technique separates dye from cloth?", "A. Extraction\nB. Chromatography\nC. Evaporation\nD. Filtration", "b"),
        ("Separating grain from chaff is called", "A. Winnowing\nB. Sieving\nC. Threshing\nD. Picking", "a")
    ],
    "Biology": [ # Topic 1: Cell: The Basic Unit of Life
        ("Powerhouse of the cell", "A. Nucleus\nB. Mitochondria\nC. Ribosome\nD. Vacuole", "b"),
        ("Cell organelle that contains chlorophyll", "A. Mitochondria\nB. Chloroplast\nC. Lysosome\nD. Golgi body", "b"),
        ("Which is not found in plant cell?", "A. Cell wall\nB. Centriole\nC. Chloroplast\nD. Large vacuole", "b"),
        ("DNA is found in the", "A. Cytoplasm\nB. Nucleus\nC. Cell membrane\nD. Vacuole", "b"),
        ("Function of ribosome", "A. Respiration\nB. Protein synthesis\nC. Digestion\nD. Storage", "b"),
        ("The smallest unit of life", "A. Tissue\nB. Organ\nC. Cell\nD. Organelle", "c"),
        ("Which cell has no nucleus?", "A. Nerve cell\nB. Red blood cell\nC. White blood cell\nD. Muscle cell", "b"),
        ("Cell membrane is made of", "A. Cellulose\nB. Lipid and protein\nC. Chitin\nD. Starch", "b"),
        ("Organelle for digestion", "A. Lysosome\nB. Peroxisome\nC. Vacuole\nD. Plastid", "a"),
        ("Plant cells are rigid due to", "A. Cell membrane\nB. Cell wall\nC. Cytoplasm\nD. Nucleus", "b")
    ],
    "Government": [ # Topic 1: Political Concepts
        ("Power that is legally recognized is called", "A. Influence\nB. Authority\nC. Coercion\nD. Force", "b"),
        ("The process of making and enforcing laws is", "A. Politics\nB. Government\nC. Democracy\nD. Administration", "b"),
        ("Sovereignty means", "A. Rule of law\nB. Supreme power\nC. Separation of powers\nD. Fundamental rights", "b"),
        ("A system where people elect representatives is", "A. Direct democracy\nB. Indirect democracy\nC. Monarchy\nD. Oligarchy", "b"),
        ("The first political party in Nigeria was", "A. NCNC\nB. NNDP\nC. AG\nD. NPC", "b"),
        ("Fundamental human rights are contained in Chapter ___", "A. II\nB. III\nC. IV\nD. V", "c"),
        ("Pressure groups aim to", "A. Win elections\nB. Influence government\nC. Make laws\nD. Judge cases", "b"),
        ("Arms of government are ___", "A. 2\nB. 3\nC. 4\nD. 5", "b"),
        ("Citizenship by birth is called", "A. Naturalization\nB. Registration\nC. Jus soli\nD. Honorary", "c"),
        ("The 1999 constitution is ___ constitution", "A. Parliamentary\nB. Presidential\nC. Monarchical\nD. Military", "b")
    ],
    "Economics": [ # Topic 1: Basic Economic Concepts
        ("The central problem of economics is", "A. Inflation\nB. Scarcity\nC. Unemployment\nD. Poverty", "b"),
        ("Opportunity cost is", "A. Total cost\nB. Next best alternative forgone\nC. Money cost\nD. Fixed cost", "b"),
        ("Land as a factor of production is rewarded with", "A. Wages\nB. Interest\nC. Rent\nD. Profit", "c"),
        ("A want that can be satisfied is called", "A. Need\nB. Effective demand\nC. Human want\nD. Commodity", "b"),
        ("The reward for entrepreneurship is", "A. Salary\nB. Interest\nC. Profit\nD. Dividend", "c"),
        ("Goods used for further production are", "A. Consumer goods\nB. Capital goods\nC. Free goods\nD. Inferior goods", "b"),
        ("The study of individual units is", "A. Macroeconomics\nB. Microeconomics\nC. Econometrics\nD. Statistics", "b"),
        ("What you give up to get something else", "A. Price\nB. Cost\nC. Opportunity cost\nD. Budget", "c"),
        ("Basic economic problem arises due to", "A. Unlimited resources\nB. Unlimited wants\nC. Limited wants\nD. Government policy", "b"),
        ("Utility means", "A. Price\nB. Satisfaction\nC. Cost\nD. Demand", "b")
    ],
    "Literature": [ # Topic 1: Oral Literature
        ("Oral literature is passed down by", "A. Writing\nB. Printing\nC. Word of mouth\nD. Recording", "c"),
        ("A short story with a moral lesson is", "A. Epic\nB. Ballad\nC. Fable\nD. Ode", "c"),
        ("Heroic poem that tells of a hero's deeds", "A. Sonnet\nB. Epic\nC. Elegy\nD. Lyric", "b"),
        ("Proverbs are examples of", "A. Drama\nB. Poetry\nC. Oral literature\nD. Novel", "c"),
        ("A story told to explain natural phenomena", "A. Myth\nB. Legend\nC. Fable\nD. Ballad", "a"),
        ("Chants used in worship are called", "A. Ballads\nB. Incantations\nC. Epics\nD. Tales", "b"),
        ("Oral poetry with rhythmic repetition", "A. Sonnet\nB. Dirge\nC. Chant\nD. Ode", "c"),
        ("Story about the past with some truth", "A. Myth\nB. Legend\nC. Fable\nD. Joke", "b"),
        ("Praise song for a king", "A. Dirge\nB. Panegyric\nC. Elegy\nD. Ballad", "b"),
        ("Riddles test one's", "A. Strength\nB. Wisdom\nC. Beauty\nD. Speed", "b")
    ],
    "CRS": [ # Topic 1: God and Man in the Beginning
        ("Who created man?", "A. Angel\nB. God\nC. Adam\nD. Moses", "b"),
        ("The first man and woman were", "A. Cain and Abel\nB. Abraham and Sarah\nC. Adam and Eve\nD. Isaac and Rebecca", "c"),
        ("Man was created in the ___ of God", "A. Likeness\nB. Image\nC. Shadow\nD. Form", "b"),
        ("The garden where Adam and Eve lived", "A. Gethsemane\nB. Eden\nC. Sinai\nD. Zion", "b"),
        ("Who tempted Eve?", "A. Cain\nB. Serpent\nC. Angel\nD. God", "b"),
        ("The consequence of sin was", "A. Blessing\nB. Death\nC. Wealth\nD. Joy", "b"),
        ("God provided clothes made of", "A. Cotton\nB. Linen\nC. Animal skin\nD. Leaves", "c"),
        ("Who was the first child of Adam and Eve?", "A. Seth\nB. Cain\nC. Abel\nD. Noah", "b"),
        ("God rested on the ___ day", "A. 6th\nB. 7th\nC. 1st\nD. 3rd", "b"),
        ("The tree in the middle of Eden was", "A. Tree of life\nB. Tree of knowledge\nC. Apple tree\nD. Fig tree", "b")
    ]
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

def get_base_css(r="255",g="215",b="0"):
    color_rgb = f"{r},{g},{b}"
    return f"""<style> @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap'); body {{font-family: 'Poppins', sans-serif; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f4f7fb;}}.container {{background:white; padding:30px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.15); width:90%; max-width:800px;}} h1 {{color:#1a3b6d; text-align:center; margin-bottom:10px;}}.logo {{width:120px; display:block; margin:0 auto 15px;}}.user-greet {{text-align:center; color:#1a3b6d; font-weight:600; margin-bottom:20px; font-size:18px;}} input, select, button {{width:100%; padding:14px; margin-top:12px; border-radius:10px; border:1px solid #ccc; font-size:16px; box-sizing:border-box;}} button {{background:#1a3b6d; color:white; border:none; cursor:pointer; font-weight:600; transition:0.3s;}} button:hover {{background:#0f274d; transform:translateY(-2px);}}.timer {{background:#ff4757; color:white; padding:12px; border-radius:10px; text-align:center; font-weight:700; font-size:18px; margin-bottom:15px;}}.question-box {{background:#f8f9ff; padding:20px; border-radius:12px; border-left:5px solid #1a3b6d; margin-bottom:20px;}}.question-title {{font-size:20px; font-weight:600; color:#1a3b6d; margin-bottom:15px;}}.options label {{display:block; background:white; padding:14px; margin:10px 0; border-radius:10px; border:2px solid #e0e0e0; cursor:pointer; transition:0.2s; font-size:16px;}}.options label:hover {{border-color:#1a3b6d; background:#f0f4ff;}}.options input[type="radio"] {{display:none;}}.options label:has(input:checked) {{border-color:#1a3b6d; background:#e8eeff; font-weight:700;}}.progress {{height:8px; background:#e0e0e0; border-radius:10px; margin-bottom:20px;}}.progress-bar {{height:8px; background:#1a3b6d; border-radius:10px; transition:width 0.3s;}} table {{width:100%; border-collapse: collapse; margin-top:20px; font-size:14px;}} th, td {{padding:10px; border:1px solid #ddd; text-align:center;}} th {{background:#1a3b6d; color:white;}} a {{color:#1a3b6d; text-decoration:none; font-weight:600; margin-right:10px;}}.correct {{color:green; font-weight:700;}}.wrong {{color:red; font-weight:700;}}

.home-body {{background:#0a0a0a; min-height:100vh; position:relative; overflow:hidden;}}
.home-body::before {{content:''; position:absolute; top:0; left:0; width:100%; height:100%; background:radial-gradient(2px 2px at 20px 30px, rgb({color_rgb}), transparent), radial-gradient(2px 2px at 40px 70px, #fff, transparent), radial-gradient(2px 2px at 50px 160px, rgb({color_rgb}), transparent), radial-gradient(2px 2px at 120px 40px, #fff, transparent), radial-gradient(3px 3px at 130px 80px, rgb({color_rgb}), transparent), radial-gradient(2px 2px at 160px 120px, #fff, transparent); background-size:200px 200px; animation:twinkle 3s linear infinite; z-index:0;}}
@keyframes twinkle {{0% {{opacity:0.3;}} 50% {{opacity:1;}} 100% {{opacity:0.3;}}}}

.home-container {{background:linear-gradient(145deg, #1a1a1a, #0f0f0f); border: 1px solid rgba({color_rgb},0.2); border-radius:24px; box-shadow:0 0 20px rgba({color_rgb},0.15), inset 0 0 15px rgba({color_rgb},0.05); position:relative; z-index:1; overflow: hidden; padding: 30px;}}
.home-container::before {{content: ''; position: absolute; top: -1px; left: -1px; right: -1px; bottom: -1px; border-radius: 25px; background: linear-gradient(90deg, transparent 0%, rgba({color_rgb},0.05) 30%, rgba({color_rgb},0.6) 50%, rgba({color_rgb},0.05) 70%, transparent 100%); background-size: 300% 100%; animation: borderRipple var(--ripple-speed, 8s) linear infinite; z-index: -1; filter: blur(2px); opacity: 0.5;}}
@keyframes borderRipple {{0% {{ background-position: 0% 50%; }} 100% {{ background-position: 300% 50%; }}}}

.home-container h1 {{color:rgb({color_rgb}); text-shadow:0 0 8px rgba({color_rgb},0.5);}}
.home-container p {{color:#e5e5e5;}}
.home-container input,.home-container select {{background:#1a1a1a; color:rgb({color_rgb}); border:1px solid rgb({color_rgb});}}
.home-container input::placeholder {{color:rgba({color_rgb},0.5);}}
.home-container button {{background:linear-gradient(135deg, rgb({color_rgb}), #ffb700); color:#000; font-size:18px; font-weight:700; box-shadow:0 4px 15px rgba({color_rgb},0.4);}}
.home-container button:hover {{background:linear-gradient(135deg, #fff, rgb({color_rgb})); transform:translateY(-2px); box-shadow:0 6px 20px rgba({color_rgb},0.6);}}
.home-container a {{color:rgb({color_rgb}); text-decoration:underline;}}
.password-wrapper {{ display: flex; gap: 8px; align-items: center; }}.password-wrapper input {{ flex: 1; margin: 0; }}.icon-btn {{ padding: 10px 12px; border: none; border-radius: 8px; cursor: pointer; font-size: 18px; background: rgb({color_rgb}); color:#000; width:auto;}}.copied {{ color: rgb({color_rgb}); font-size: 12px; display: none; }}.msg {{ background: rgba({color_rgb},0.2); padding: 15px; border-radius: 8px; text-align: center; font-weight: bold; color: rgb({color_rgb}); margin: 15px 0; border:1px solid rgb({color_rgb});}}
.dark-table th {{background:rgb({color_rgb}); color:#000; font-weight:700;}}
.dark-table tr {{background:#1a1a1a;}}
.dark-table td {{color:#e5e5e5; border-color:#333;}}
@keyframes pulse {{0%{{box-shadow:0 0 0 0 rgba({color_rgb},0.7)}} 70%{{box-shadow:0 0 0 15px rgba({color_rgb},0)}} 100%{{box-shadow:0 0 0 0 rgba({color_rgb},0)}}}}
</style>"""

subject_options = "".join([f"<option>{s}</option>" for s in ALL_QUESTIONS])

def render_page(template, color_rgb="255,215,0", **kwargs):
    r,g,b = color_rgb.split(",")
    return render_template_string(get_base_css(r,g,b) + template, **kwargs)

LOGIN_TEMPLATE = """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><img src="{{ url_for('static', filename='raven.png') }}" class="logo" style="width:100px; filter:drop-shadow(0 0 15px rgba(255,215,0,0.8))"><h1 style="font-size:28px; margin-bottom:8px">Scholars'Haven</h1><p style="text-align:center; color:rgba(255,215,0,0.8); margin-bottom:30px; font-weight:600">UTME CBT Portal | Excellence Through Knowledge</p>{% if error %}<p style="background:rgba(255,0,0,0.2); color:#ffd700; padding:10px; border-radius:8px; text-align:center; border:1px solid #ffd700">{{error}}</p>{% endif %}<form method="POST"><input name="name" placeholder="👤 Full Name" required><input type="password" name="password" placeholder="🔒 Password" required><button>Login →</button></form><p style="text-align:center; margin-top:20px"><a href="/register">New Student?</a> | <a href="/admin">Admin</a></p></div></body>"""

REGISTER_TEMPLATE = """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><h1>📝 Create Account</h1><form method="POST"><input name="name" placeholder="👤 Enter your full name" required>{% if password %}<div class="password-wrapper"><input type="password" id="passwordField" value="{{password}}" readonly><button type="button" class="icon-btn" onclick="togglePassword()" title="Show/Hide">👁️</button><button type="button" class="icon-btn" onclick="copyPassword()" title="Copy">📋</button></div><span id="copiedText" class="copied">Copied!</span><div class="msg">✅ Account Created! Save this password: <b>{{password}}</b></div>{% endif %}<button type="submit">Generate Password</button></form>{% if error %}<div class="msg" style="background:rgba(255,0,0,0.2);">{{error}}</div>{% endif %}<p style="text-align:center; margin-top:15px"><a href="/">Already have account? Login</a></p><script>function togglePassword() {var x = document.getElementById("passwordField"); x.type = x.type === "password"? "text" : "password";} function copyPassword() {var x = document.getElementById("passwordField"); navigator.clipboard.writeText(x.value); document.getElementById("copiedText").style.display = "inline"; setTimeout(() => { document.getElementById("copiedText").style.display = "none"; }, 2000);}</script></div></body>"""

QUIZ_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>Scholars'Haven: {{subject}}</h1><div class="user-greet">Hi {{user_name}} 👋</div><div class="progress"><div class="progress-bar" style="width: {{progress}}%"></div></div><div class="timer">⏱ Time Left: <span id="timer">{{time_left}}</span> seconds</div><form method="POST"><div class="question-box"><div class="question-title">Question {{q_num}} of {{total_q}}</div><div>{{question.prompt}}</div></div><div class="options">{% for opt in question.options.split('\\n') %}<label><input type="radio" name="answer" value="{{opt[0]}}" required><span>{{opt}}</span></label>{% endfor %}</div><button>Next Question →</button></form><script>let time = {{time_left}};let timer = setInterval(()=>{time--;document.getElementById('timer').innerText = time;if(time <= 0){clearInterval(timer); document.querySelector('form').submit();}}, 1000)</script></div></body>"""

ADMIN_LOGIN_TEMPLATE = """<body class="home-body"><div class="container home-container" style="padding:40px 30px; max-width:450px"><h1>🔐 Admin Login</h1>{% if error %}<p style="background:rgba(255,0,0,0.2); color:#ffd700; padding:10px; border-radius:8px; text-align:center; border:1px solid #ffd700">{{error}}</p>{% endif %}<form method="POST"><input type="password" name="password" placeholder="Enter Admin Password" required><button>Login</button></form></div></body>"""

ADMIN_TEMPLATE = """<body class="home-body"><div class="container home-container" style="max-width:1000px"><h1>👑 Admin Panel v3.2.7L</h1><p style="font-weight:700; text-align:center">✅ 90 UTME QUESTIONS LOADED</p><div style="display:flex; justify-content:space-between; margin-bottom:15px; flex-wrap:wrap; gap:10px"><a href="/wipe_db" onclick="return confirm('DANGER: This will DELETE ALL USERS AND ATTEMPTS.')" style="background:#ff4757; color:white; padding:12px 20px; border-radius:8px; font-weight:700; text-decoration:none">🗑️ WIPE ENTIRE DB</a><a href="/logout" style="background:#ffd700; color:#000; padding:12px 20px; border-radius:8px; font-weight:700; text-decoration:none">Logout</a></div><div style="overflow-x:auto"><table class="dark-table"><tr><th>Name</th><th>Password</th><th>Subject Taken</th><th>Score</th><th>Music</th><th>Actions</th></tr>{% for u in users %}<tr><td>{{u.name.title()}}</td><td style="font-weight:700">{{u.password}}</td><td>{{u.subject if u.subject else '-'}}</td><td style="font-weight:700">{{u.score}}/10</td><td>{{'🔊 ON' if u.music_on else '🔇 OFF'}}</td><td><a href="/reset_user/{{u.id}}" style="color:#ff4757; font-weight:700;">Delete</a></td></tr>{% endfor %}</table></div></div></body>"""

SUBMIT_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>Submitted ✅</h1><p style="text-align:center; font-size:18px">Thank you {{name}}!<br>Score: {{score}}/{{total_q}}<br>You cannot take any other subject again.</p><a href="/" style="display:block; text-align:center; margin-top:20px; background:#ffd700; color:#000; padding:12px; border-radius:8px; font-weight:700">Back to Login</a></div></body>"""

@app.route("/init")
def init_db():
    with app.app_context():
        db.session.execute(db.text('DROP TABLE IF EXISTS "attempt" CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS "question" CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS "user" CASCADE'))
        db.session.commit()
        db.create_all()
        count = load_questions()
    return render_page(f"<body class='home-body'><div class='container home-container'><h1 style='text-align:center'>Database RESET ✅</h1><p style='text-align:center; font-size:18px'>Loaded {count} questions. All old users deleted.</p><a href='/' style='background:#ffd700; color:#000; padding:12px 20px; border-radius:8px; font-weight:700; display:block; text-align:center'>Go Home</a></div></body>")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"].lower().strip()
        password = request.form["password"]
        user = User.query.filter_by(name=name, password=password).first()
        if user:
            session["user_id"] = user.id; session["user_name"] = user.name; session["music_on"] = user.music_on
            return redirect("/home")
        else: return render_page(LOGIN_TEMPLATE, error="Invalid Name or Password")
    return render_page(LOGIN_TEMPLATE, error=None)

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
    return render_page(REGISTER_TEMPLATE, password=password, error=error)

@app.route("/home")
def home():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    user_name = session['user_name'].title()
    music_state = "ON" if session.get("music_on") else "OFF"
    music_icon = "🔊" if session.get("music_on") else "🔇"
    html = f"""<body class="home-body">
    <audio id="bgMusic" loop preload="metadata">
        <source src="{{{{ url_for('static', filename='lofi.mp3') }}}}" type="audio/mpeg">
    </audio>
    <div class="container home-container">
        <h1>Welcome {user_name}</h1>
        <p style="text-align:center; font-weight:600">UTME CBT |@app.route("/home")
def home():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    user_name = session['user_name'].title()
    music_state = "ON" if session.get("music_on") else "OFF"
    music_icon = "🔊" if session.get("music_on") else "🔇"
    html = f"""<body class="home-body">
    <audio id="bgMusic" loop preload="metadata">
        <source src="{{{{ url_for('static', filename='lofi.mp3') }}}}" type="audio/mpeg">
    </audio>
    <div class="container home-container">
        <h1>Welcome {user_name}</h1>
        <p style="text-align:center; font-weight:600">UTME CBT | 10 Questions | 3 Minutes | 1 ATTEMPT TOTAL</p>
        <button id="musicBtn" onclick="toggleMusic()" style="width:auto; padding:14px 25px; font-size:16px; margin:0 auto 20px; display:block; animation:pulse 2s infinite">{music_icon} Music: {music_state}</button>
        <p id="musicStatus" style="text-align:center; font-size:12px; color:rgba(255,215,0,0.7); margin-top:-10px; margin-bottom:20px;"></p>
        <form method="POST" action="/start_quiz">
            <select name="subject" required>
                <option value="">-- Select Subject --</option>
                {subject_options}
            </select>
            <button>Start Quiz</button>
        </form>
        <p style="text-align:center; margin-top:20px"><a href="/logout">Logout</a></p>
    </div>
    <script>
        const audio = document.getElementById('bgMusic');
        const btn = document.getElementById('musicBtn');
        const status = document.getElementById('musicStatus');
        let musicOn = {str(session.get("music_on", False)).lower()};
        
        function updateBtn() {{
            if(musicOn) {{
                btn.innerHTML = '🔊 Music: ON';
                btn.style.animation = 'pulse 2s infinite';
                status.innerText = 'Tap anywhere if music does not play';
            }} else {{
                btn.innerHTML = '🔇 Music: OFF';
                btn.style.animation = 'none';
                status.innerText = '';
            }}
        }}
        
        function toggleMusic() {{
            musicOn = !musicOn;
            fetch('/toggle_music', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{state: musicOn}})
            }});
            if(musicOn) {{ audio.play().catch(()=>{{}}) }} else {{ audio.pause(); }}
            updateBtn();
        }}
        
        document.addEventListener('click', () => {{ if(musicOn) audio.play().catch(()=>{{}}) }}, {{once: true}});
        updateBtn();
    </script>
    </body>"""
    return render_page(html)

@app.route("/toggle_music", methods=["POST"])
def toggle_music():
    if "user_id" not in session: return {"status": "error"}, 401
    data = request.get_json()
    state = data.get("state", False)
    session["music_on"] = state
    user = User.query.get(session["user_id"])
    user.music_on = state
    db.session.commit()
    return {"status": "ok"}

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if user.has_attempted: return render_page(f"<body class='home-body'><div class='container home-container'><h1>Already Attempted</h1><p>Hi {user.name.title()}, you have already taken {user.subject}. 1 attempt total only.</p><a href='/home'>Go Home</a></div></body>")
    
    subject = request.form["subject"]
    session["subject"] = subject
    subject_questions = Question.query.filter_by(subject=subject).all()

    if len(subject_questions) == 0:
        return render_page(f"<body class='home-body'><div class='container home-container'><h1>⚠️ No Questions Found</h1><p>There are 0 questions for {subject} in the database.</p><p>Fix: Visit /init</p><a href='/home'>Go Back</a></div></body>", color_rgb="255,71,87")

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
    questions = [Question.query.get(qid) for qid in question_ids]
    questions = [q for q in questions if q is not None]
    
    q_index = session["q_index"]
    total_q = session.get("total_q", len(questions))
    
    if len(questions) == 0:
        return render_page(f"<body class='home-body'><div class='container home-container'><h1>⚠️ Quiz Error</h1><p>No questions found for {session.get('subject', 'this subject')}.</p><p>Please go to /init and reload questions.</p><a href='/home'>Go Back</a></div></body>", color_rgb="255,71,87")

    if q_index >= total_q or q_index >= len(questions): 
        return redirect("/submit")
    
    if request.method == "POST":
        ans = request.form["answer"].lower().strip()
        session["answers"][str(q_index+1)] = ans
        if ans == questions[q_index].answer: session["score"] += 1
        session["q_index"] += 1
        session.modified = True
        return redirect(f"/quiz?color={request.args.get('color', '255,215,0')}")
    
    progress = int((q_index / total_q) * 100) if total_q > 0 else 0
    color_rgb = request.args.get('color', '255,215,0')
    return render_page(QUIZ_TEMPLATE, color_rgb=color_rgb, subject=session["subject"], question=questions[q_index], q_num=q_index+1, total_q=total_q, time_left=time_left, progress=progress, user_name=session["user_name"].title())

@app.route("/submit")
def submit():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if not user.has_attempted:
        user.has_attempted = True
        user.score = session.get("score", 0)
        user.submitted_at = time.time()
        attempt = Attempt(user_id=user.id, subject=session.get("subject"), answers_json=json.dumps(session.get("answers", {})), score=user.score, submitted_at=user.submitted_at)
        db.session.add(attempt)
        db.session.commit()
    return render_page(SUBMIT_TEMPLATE, name=session["user_name"].title(), score=user.score, total_q=session.get("total_q", 10))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin_panel")
        else:
            return render_page(ADMIN_LOGIN_TEMPLATE, error="Wrong Password")
    return render_page(ADMIN_LOGIN_TEMPLATE, error=None)

@app.route("/admin_panel")
def admin_panel():
    if not session.get("admin"): return redirect("/admin")
    users = User.query.order_by(User.id.desc()).all()
    return render_page(ADMIN_TEMPLATE, users=users)

@app.route("/reset_user/<int:user_id>")
def reset_user(user_id):
    if not session.get("admin"): return redirect("/admin")
    user = User.query.get(user_id)
    if user:
        Attempt.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
    return redirect("/admin_panel")

@app.route("/wipe_db")
def wipe_db():
    if not session.get("admin"): return redirect("/admin")
    with app.app_context():
        db.session.execute(db.text('DROP TABLE IF EXISTS "attempt" CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS "question" CASCADE'))
        db.session.execute(db.text('DROP TABLE IF EXISTS "user" CASCADE'))
        db.session.commit()
        db.create_all()
        load_questions()
    return redirect("/admin_panel")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)