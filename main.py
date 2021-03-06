from flask import Flask, render_template, request, redirect, url_for, make_response
from model import User, db
import random
import uuid
import hashlib

app = Flask(__name__)
db.create_all()


@app.route("/")
def index():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if session_token and user.delete == "no":
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return render_template("index.html", user=user)

@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    secret_num = random.randint(1, 50)
    password = request.form.get("user-password")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    delete = "no"

    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, secret_num=secret_num, password=hashed_password, delete=delete)
        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return "Wrong Password"

    elif user.delete == "no":

        session_token = str(uuid.uuid4())
        user.session_token = session_token

        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response

    else:
        return redirect(url_for("logout"))


@app.route("/guess", methods=["POST"])
def guess():

    guess = int(request.form.get("your-guess"))
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if not guess:
        return "Please choose a number between 1 - 50"

    elif guess == user.secret_num:
        message = "Success.  You guessed correctly"
        user.secret_num = random.randint(1, 50)

        db.add(user)
        db.commit()

    elif guess < user.secret_num:
        message = "Try a bigger number"
    else:
        message = "Try a smaller number"

    return render_template("results.html", message=message)


@app.route("/logout", methods=["GET", "POST"])
def logout():

    session_token = ""

    response = make_response(redirect(url_for('index')))
    response.set_cookie("session_token", session_token)

    return response


@app.route("/profile", methods=["GET"])
def profile():

    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index"))


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":

        if user:
            return render_template("profile_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":

        name = request.form.get("profile-name")
        email = request.form.get("profile-email")

        user.name = name
        user.email = email

        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":

        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":

        user.delete = "yes"
        db.commit()

        return redirect(url_for("logout"))


@app.route("/users", methods=["GET"])
def all_users():

    delete = "no"
    valid_users = db.query(User).filter_by(delete=delete).all()

    return render_template("users.html", users=valid_users)


@app.route("/user/<user_id>", methods=["GET"])
def user_details(user_id):

    user = db.query(User).get(int(user_id))

    return render_template("user_details.html", user=user)


@app.route("/password/edit", methods=["GET", "POST"])
def password_edit():

    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":

        if user:
            return render_template("password_edit.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":

        current_password = request.form.get("current-password")
        hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()

        if hashed_current_password != user.password:
            return "Wrong Current Password"
        else:
            return render_template("password_check.html")


@app.route("/password/check", methods=["GET", "POST"])
def password_check():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    new_password = request.form.get("new-password")
    new_password2 = request.form.get("new-password2")

    if new_password != new_password2:
        return "The Passwords Do Not Match"
    else:

        user.password = hashlib.sha256(new_password.encode()).hexdigest()
        session_token = str(uuid.uuid4())
        user.session_token = session_token

        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('profile')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response


if __name__ == '__main__':
    app.run()