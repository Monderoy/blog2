from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "123456"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# hur länge vi är inloggade
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

# skapar ett unikt id (int) i en column i db
class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
# tar bort värden som inte har ett värde? en obesvarad fråga?
    def __init__(self, name, email):
        self.name = name
        self.email = email

@app.route("/")
def home():
    return render_template("index.html")

# så vi kan se alla som har ett konto
@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

# skapar en login-ruta där man kan skriva in sin mail, spara i db som kan hämta tillbaka det första vi hittar i db

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
                usr = users(user, "")
                db.session.add(usr)
                db.session.commit()

        flash("login Succesful")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in")
            return redirect(url_for("user"))

        return render_template("login.html")

# vi hämtar tillbaka användarens namn och skriver ut det, är man inte inloggad skickas man till login
# vi kollar i db efter mailen, fins den inte så sparas den
@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit()
            flash("Email was saved")
        else:
            if "email" in session:
                email = session["email"]

        return render_template("user.html", email=email)
    else:
        flash("you are not logged in")
        return redirect(url_for("login"))


# logga ut och skicka tillbaka till login, vi pop:ar den så emailen rensas
@app.route("/logout")
def logout():
    flash(f"You have been logged out", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author = db.Column(db.String(20), nullable=False)

@app.route("/blog")
def blog():
    posts = Post.query.all()
    return render_template("blog.html", posts=posts)

@app.route("/blog/new", methods=["GET", "POST"])
def new_post():
    if "user" not in session:
        flash("You need to log in before you can create a new post")
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        author = request.form["auther"]
        post = Post(title=title, content=content, author=author)
        db.session.add(post)
        db.session.commit()
        flash("New post created")
        return redirect(url_for("blog"))
    else:
        return render_template("new_post:html")



if __name__ =="__main__":
    db.create_all()
    app.run(debug=True)


