from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import time
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "scholars_haven_secret_2026"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

QUIZ_DURATION = 180 # 3 minutes
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
    "Maths - Law of Indices": [
        ("Simplify: 2^3 x 2^4", "a) 2^7\nb) 2^12\nc) 4^7\nd) 8^7", "a"),
        ("Express 1/32 as a power of 2", "a) 2^-3\nb) 2^-4\nc) 2^-5\nd) 2^-6", "c"),
        ("If 3^x = 27, what is x?", "a) 2\nb) 3\nc) 4\nd) 9", "b"),
        ("Simplify: (5^2)^3", "a) 5^5\nb) 5^6\nc) 10^6\nd) 25^3", "b"),
        ("Evaluate: 8^(2/3)", "a) 2\nb) 3\nc) 4\nd) 8", "c"),
        ("Simplify: a^5 / a^2", "a) a^3\nb) a^7\nc) a^10\nd) a^2", "a"),
        ("If 2^n = 64, find n", "a) 4\nb) 5\nc) 6\nd) 8", "c"),
        ("Simplify: (2x^3)^2", "a) 2x^6\nb) 4x^5\nc) 4x^6\nd) 2x^5", "c"),
        ("Express 0.125 as a power of 2", "a) 2^-1\nb) 2^-2\nc) 2^-3\nd) 2^-4", "c"),
        ("Find the value of: 9^(1/2)", "a) 3\nb) 9\nc) 18\nd) 81", "a")
    ],
    "English - Concord": [
        ("The list of items ___ on the table.", "a) are\nb) is\nc) were\nd) have", "b"),
        ("Neither John nor his friends ___ present.", "a) is\nb) are\nc) was\nd) were", "b"),
        ("Each of the students ___ to submit an assignment.", "a) have\nb) has\nc) are\nd) were", "b"),
        ("The committee ___ divided on the issue.", "a) is\nb) are\nc) was\nd) has", "b"),
        ("A number of students ___ absent today.", "a) is\nb) was\nc) are\nd) has", "c"),
        ("Either the manager or the clerks ___ to sign.", "a) has\nb) have\nc) is\nd) was", "b"),
        ("Bread and butter ___ my breakfast.", "a) are\nb) is\nc) were\nd) have", "b"),
        ("The news ___ shocking.", "a) are\nb) were\nc) is\nd) have", "c"),
        ("Everyone of us ___ a responsibility.", "a) have\nb) has\nc) are\nd) were", "b"),
        ("Ten thousand naira ___ a lot of money.", "a) are\nb) were\nc) is\nd) have", "c")
    ],
    "Chemistry - Atom, Molecule, Ion": [
        ("Which of the following represents an atom?", "a) H2\nb) Na+\nc) H2O\nd) Na", "d"),
        ("A molecule of water contains ___ atoms.", "a) 1\nb) 2\nc) 3\nd) 4", "c"),
        ("Na+ is an example of a ___", "a) Molecule\nb) Atom\nc) Cation\nd) Anion", "c"),
        ("Which particle has no charge?", "a) Proton\nb) Electron\nc) Neutron\nd) Ion", "c"),
        ("Cl- is formed when chlorine ___ an electron.", "a) loses\nb) shares\nc) gains\nd) destroys", "c"),
        ("The smallest particle of a compound that can exist is a ___", "a) Atom\nb) Molecule\nc) Ion\nd) Element", "b"),
        ("How many atoms are in CO2?", "a) 1\nb) 2\nc) 3\nd) 4", "c"),
        ("Which of these is NOT an ion?", "a) Ca2+\nb) O2-\nc) H2O\nd) K+", "c"),
        ("An atom becomes a cation by ___", "a) gaining electrons\nb) losing electrons\nc) gaining protons\nd) losing neutrons", "b"),
        ("H2SO4 is a ___", "a) Atom\nb) Ion\nc) Molecule\nd) Element", "c")
    ]
}

def cleanup_old_records():
    cutoff = time.time() - (24 * 3600)
    old_attempts = Attempt.query.filter(Attempt.submitted_at < cutoff).all()
    for a in old_attempts:
        db.session.delete(a)
        user = User.query.get(a.user_id)
        if user: db.session.delete(user)
    db.session.commit()

with app.app_context():
    db.create_all()
    cleanup_old_records()
    if Question.query.count() == 0:
        for subject, questions in ALL_QUESTIONS.items():
            for q, opts, a in questions:
                db.session.add(Question(subject=subject, prompt=q, options=opts, answer=a))
        db.session.commit()

@app.route("/", methods=["GET", "POST"])
def home():
    cleanup_old_records()
    if request.method == "POST":
        name = request.form["name"].strip()
        subject = request.form["subject"]
        user = User.query.filter_by(name=name, subject=subject).first()
        if not user: 
            user = User(name=name, subject=subject)
            db.session.add(user)
            db.session.commit()
        if user.has_attempted: 
            return render_template("already.html", subject=subject)
        session["user_id"] = user.id
        session["q_index"] = 0
        session["score"] = 0
        session["answers"] = {}
        session["subject"] = subject
        user.start_time = time.time()
        db.session.commit()
        return redirect("/quiz")
    return render_template("home.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    user = User.query.get(session["user_id"])
    if time.time() - user.start_time > QUIZ_DURATION: 
        return redirect("/submit")
    time_left = int(QUIZ_DURATION - (time.time() - user.start_time))
    questions = Question.query.filter_by(subject=session["subject"]).all()
    q_index = session["q_index"]
    if q_index >= len(questions): 
        return redirect("/submit")
    if request.method == "POST":
        ans = request.form["answer"].lower().strip()
        session["answers"][str(q_index+1)] = ans
        if ans == questions[q_index].answer: 
            session["score"] += 1
        session["q_index"] += 1
        session.modified = True
        return redirect("/quiz")
    progress = int((q_index / len(questions)) * 100)
    return render_template("quiz.html", subject=session["subject"], question=questions[q_index], 
                           q_num=q_index+1, time_left=time_left, progress=progress)

@app.route("/submit")
def submit():
    user = User.query.get(session["user_id"])
    user.score = session["score"]
    user.has_attempted = True
    user.submitted_at = time.time()
    attempt = Attempt(user_id=user.id, subject=session["subject"], 
                      answers_json=json.dumps(session["answers"]), 
                      score=session["score"], submitted_at=time.time())
    db.session.add(attempt)
    db.session.commit()
    return render_template("submit.html", name=user.name, subject=session["subject"])

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect("/admin_panel")
        else: 
            return render_template("admin_login.html", error="Wrong Password")
    return render_template("admin_login.html", error=None)

@app.route("/admin_panel")
def admin_panel():
    if not session.get('is_admin'): 
        return redirect("/admin")
    cleanup_old_records()
    attempts = Attempt.query.all()
    for a in attempts:
        a.user_name = User.query.get(a.user_id).name
        a.sub_time = datetime.fromtimestamp(a.submitted_at).strftime('%d-%b %H:%M')
    return render_template("admin.html", attempts=attempts)

@app.route("/review/<int:attempt_id>")
def review(attempt_id):
    if not session.get('is_admin'): 
        return redirect("/admin")
    attempt = Attempt.query.get(attempt_id)
    user = User.query.get(attempt.user_id)
    questions = Question.query.filter_by(subject=attempt.subject).all()
    answers = json.loads(attempt.answers_json)
    review_data = []
    for i, q in enumerate(questions):
        q_num = str(i+1)
        review_data.append({
            "num": q_num, "prompt": q.prompt, "correct": q.answer.upper(),
            "student": answers.get(q_num, "No Answer").upper(),
            "is_correct": answers.get(q_num) == q.answer
        })
    return render_template("review.html", user_name=user.name, subject=attempt.subject, 
                           score=attempt.score, review_data=review_data)

@app.route("/reset/<int:attempt_id>")
def reset(attempt_id):
    if not session.get('is_admin'): 
        return "Unauthorized"
    attempt = Attempt.query.get(attempt_id)
    user = User.query.get(attempt.user_id)
    db.session.delete(attempt)
    db.session.delete(user)
    db.session.commit()
    return redirect("/admin_panel")

@app.route("/logout")
def logout(): 
    session.pop('is_admin', None)
    return redirect("/")

if __name__ == "__main__": 
    app.run(host="0.0.0.0", port=5000, debug=False)
