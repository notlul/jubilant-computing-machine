from flask import Flask,render_template, request, session, jsonify, redirect
from tinydb import TinyDB, Query


app = Flask(__name__)
app.secret_key = "test_test"

db = TinyDB("db/db.json")
users = db.table("users")
User = Query()


@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    return redirect("/dashboard")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    user = request.form.get("user")
    psw = request.form.get("pass")
    if users.search((User.username == user) & (User.password == psw)):
        session["user"] = user
        return redirect("/dashboard")

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
            "notes" : []
        })
        return redirect("/login")
    return render_template("register.html") 
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/saveNote/<note>", methods = ["POST"])
def saveNote(note):
    user = session["user"]
    if not user:
        return redirect("/login")
    userData = users.get(User.username == user)
    notes = userData.get("notes", [])
    notes.append(note)
    users.update({'notes': notes}, User.username == user)

@app.route("/removeNote/<note>", methods = ["POST"])
def removeNote(note):
    user = session["user"]
    if not user:
        return redirect("/login")
    userData = users.get(User.username == user)
    notes = userData.get("notes", [])
    notes.remove(note)
    users.update({'notes': notes}, User.username == user)

@app.route("/getNotes", methods = ["GET"])
def getNotes():
    user = session["user"]
    if not user:
        return redirect("/login")
    notes = users.get(User.username == user).get("notes", [])
    return jsonify(notes)
if __name__ == "__main__":
    app.run(debug=True)