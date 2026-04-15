from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import random
import ollama
import re

app = Flask(__name__, template_folder="templates2")
app.secret_key = "test_test"

base_dir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    c1 = db.Column(db.Integer, default=0)
    c2 = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name,
            "option1": self.option1, "option2": self.option2,
            "c1": self.c1, "c2": self.c2
        }

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    username = request.form.get("user")
    psw = request.form.get("pass")
    
    user = User.query.filter_by(username=username, password=psw).first()
    if user:
        session["user"] = username
        return redirect("/")
    return "Invalid Credentials", 401

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form.get("user")
    psw = request.form.get("pass")
    
    if not User.query.filter_by(username=username).first():
        new_user = User(username=username, password=psw)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/creator")
def creator():
    if "user" not in session:
        return redirect("/login")
    return render_template("create.html")

@app.route("/getQuestion")
def getQuestion():
    all_qs = Question.query.all()
    if not all_qs:
        return jsonify({"error": "No questions yet"}), 404
    q = random.choice(all_qs)
    return jsonify(q.to_dict())

@app.route("/createQuestion/<name>/<option1>/<option2>", methods=["POST"])
def createQuestion(name, option1, option2):
    new_q = Question(name=name, option1=option1, option2=option2)
    db.session.add(new_q)
    db.session.commit()
    return redirect("/")

@app.route("/vote/<int:q_id>/<choice>", methods=["POST"])
def vote(q_id, choice):
    q = Question.query.get(q_id)
    if q:
        if choice == 'c1':
            q.c1 += 1
        else:
            q.c2 += 1
        db.session.commit()
        return jsonify(q.to_dict()), 200
    return jsonify({"error": "Not found"}), 404

@app.route("/genQuestion", methods=["GET"])

def genQuestion():

    if "user" not in session:

        return ["You need to be logged in", "", ""]

    response = ollama.chat(model='llama3.2:1b', messages=[

        {

            'role': 'system',

            'content': 'You are a data generator. Output: Title;Option1;Option2. Use semicolons. No intro text, no brackets.'

        },

        {

            'role': 'user',

            'content': 'Generate a weird would you rather question.'

        }

    ])





    raw_text = response['message']['content'].strip()



    clean_text = re.sub(r'^.*?:', '', raw_text)

    clean_text = clean_text.replace('[', '').replace(']', '').replace('"', '')





    parts = [item.strip() for item in clean_text.split(';') if item.strip()]



    if len(parts) == 2:

        second_part = parts[1]

        if " or " in second_part.lower():

            sub_parts = re.split(r'\s+or\s+', second_part, flags=re.IGNORECASE)

            parts = [parts[0]] + sub_parts



    if len(parts) == 1:

        temp = re.split(r'Would you rather| or ', parts[0], flags=re.IGNORECASE)

        parts = ["Would You Rather"] + [p.strip() for p in temp if p.strip()]



    final_parts = []

    for i, p in enumerate(parts):

        cleaned = p.replace("Would you rather", "").replace("would you rather", "").strip()

        if cleaned:

            final_parts.append(cleaned[0].upper() + cleaned[1:])



    if not final_parts[0].startswith("Would"):

        final_parts.insert(0, "Would You Rather")



    return jsonify(final_parts[:3])

if __name__ == "__main__":
    app.run(debug=True)