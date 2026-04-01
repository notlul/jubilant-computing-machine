from flask import Flask,render_template, request, session, jsonify, redirect
from tinydb import TinyDB, Query


app = Flask(__name__, template_folder="templates1")
app.secret_key = "test_test"

db = TinyDB("db/db1.json")
users = db.table("users")
posts = db.table("posts")
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
            "posts" : [[]]
        })
        return redirect("/login")
    return render_template("register.html") 
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/createPost", methods = ["POST"])
def saveNote():
    user = session["user"]
    if not user:
        return redirect("/login")
    currPost = []
    text = request.form.get("text")
    img = request.form.get("image")
    currPost.append(text)
    currPost.append(img)
    userData = users.get(User.username == user)
    notes = userData.get("posts", [])
    allPosts = posts.get("posts", [])
    allPosts.append(currPost)
    notes.append(currPost)
    users.update({'posts': notes}, User.username == user)
    posts.update({'allPosts': notes})
    return "OK"

@app.route("/getUserPosts", methods = ["GET"])
def getUserPosts():
    user = session["user"]
    if not user:
        return redirect("/login")
    userData = users.get(User.username == user)
    posts = userData.get("posts", [])
    print(posts)
    return jsonify(posts)
if __name__ == "__main__":
    app.run(debug=True)