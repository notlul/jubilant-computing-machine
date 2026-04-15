from flask import Flask, render_template, request, jsonify, session, redirect
from tinydb import TinyDB, Query
import os
import random
import ollama
import re

app = Flask(__name__, template_folder="templates2")
app.secret_key = "test_test"

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'db/db2.json')
db = TinyDB(db_path)
users = db.table("users")
Question = Query()
User = Query()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    psw = request.form.get("pass")
    if users.search((User.username == user) & (User.password == psw)):
        session["user"] = user
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    user = request.form.get("user")
    psw = request.form.get("pass")
    if not users.search(User.username == user):
        users.insert({
            "username" : user,
            "password" : psw,
        })
        return redirect("/login")
    return render_template("register.html") 
@app.route("/logout", methods=["GET"])
def logout():
    if "user" not in session:
        return redirect("/login")
    session.clear()
    return redirect("/")
@app.route("/creator")
def creator():
    if "user" not in session:
        return redirect("/login")
    return render_template("create.html")

@app.route("/getQuestion", methods=["GET"])
def getQuestion():
    data = db.all()
    return jsonify(data[random.randint(0,len(data)-1)])

@app.route("/createQuestion/<name>/<option1>/<option2>", methods=["POST"])
def createQuestion(name, option1, option2):
    question_id = len(db) + 1

    db.insert({
        'id': question_id,
        'name': name, 
        'option1': option1,
        'option2': option2,
        'c1': 0,
        'c2': 0
        })
    return jsonify({"status": "success"}), 200

@app.route("/vote/<int:q_id>/<choice>", methods=["POST"])
def vote(q_id, choice):
    item = db.get(Question.id == q_id)
    
    if item:
        if choice == 'c1':
            new_val = item.get('c1', 0) + 1
            db.update({'c1': new_val}, Question.id == q_id)
        else:
            new_val = item.get('c2', 0) + 1
            db.update({'c2': new_val}, Question.id == q_id)
            
        updated_item = db.get(Question.id == q_id)
        return jsonify(updated_item), 200
    
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