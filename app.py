# SCHOLARS HAVEN V3.2.7M - FIXED SYNTAX ERROR
from flask import Flask, render_template_string, request, redirect, session, url_for, jsonify
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
    "Mathematics": [
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
    "English": [
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
    "Physics": [
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
    "Chemistry": [
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
    "Biology": [
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
    "Government": [
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
    "Economics": [
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
    "Literature": [
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
    "CRS": [
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
    css = f"<style> @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap'); body {{font-family: 'Poppins', sans-serif; margin:0; padding:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#f4f7fb;}}.container {{background:white; padding:30px; border-radius:16px; box-shadow:0 8px 24px rgba(0,0,0,0.15); width:90%; max-width:800px;}}.home-body {{background:#0a0a0a;}}.home-container {{background:linear-gradient(145deg, #1a1a1a, #0f0f0f); border: 1px solid rgba({color_rgb},0.2);}} </style>"
    return css

subject_options = "".join([f"<option>{s}</option>" for s in ALL_QUESTIONS])

def render_page(template, color_rgb="255,215,0", **kwargs):
    r,g,b = color_rgb.split(",")
    return render_template_string(get_base_css(r,g,b) + template, **kwargs)

LOGIN_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>Scholars'Haven</h1>{% if error %}<p>{{error}}</p>{% endif %}<form method="POST"><input name="name" placeholder="Full Name" required><input type="password" name="password" placeholder="Password" required><button>Login</button></form></div></body>"""

REGISTER_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>Register</h1><form method="POST"><input name="name" placeholder="Full Name" required><button>Generate Password</button></form>{% if password %}<p>Password: <b>{{password}}</b></p>{% endif %}{% if error %}<p>{{error}}</p>{% endif %}</div></body>"""

QUIZ_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>{{subject}}</h1><p>Hi {{user_name}}</p><p>Question {{q_num}} of {{total_q}}</p><form method="POST"><p>{{question.prompt}}</p><div>{% for opt in question.options.split('\\n') %}<label><input type="radio" name="answer" value="{{opt[0]}}" required>{{opt}}</label>{% endfor %}</div><button>Next</button></form></div></body>"""

ADMIN_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>Admin Panel</h1><table>{% for u in users %}<tr><td>{{u.name}}</td><td>{{u.score}}</td></tr>{% endfor %}</table></div></body>"""

SUBMIT_TEMPLATE = """<body class="home-body"><div class="container home-container"><h1>Submitted</h1><p>Score: {{score}}/{{total_q}}</p></div></body>"""

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
            error = "Name already taken."
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
    html = """<body class="home-body"><div class="container home-container">
    <h1>Welcome """ + user_name + """</h1>
    <form method="POST" action="/start_quiz">
        <select name="subject" required>
            <option value="">-- Select Subject --</option>""" + subject_options + """
        </select>
        <button>Start Quiz</button>
    </form>
    </div></body>"""
    return render_page(html)

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
    return redirect("/quiz")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user_id" not in session: return redirect("/")
    if "shuffled_ids" not in session: return redirect("/home")
    
    user = User.query.get(session["user_id"])
    if time.time() - user.start_time > QUIZ_DURATION: return redirect("/submit")
    
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
        return redirect("/quiz")
    
    return render_page(QUIZ_TEMPLATE, subject=session["subject"], question=questions[q_index], q_num=q_index+1, total_q=total_q, user_name=session["user_name"].title())

@app.route("/submit")
def submit():
    if "user_id" not in session: return redirect("/")
    user = User.query.get(session["user_id"])
    if not user.has_attempted:
        user.has_attempted = True
        user.score = session.get("score", 0)
        db.session.commit()
    return render_page(SUBMIT_TEMPLATE, score=user.score, total_q=session.get("total_q", 10))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)