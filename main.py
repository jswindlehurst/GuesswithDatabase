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
    if session_token:
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


    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, secret_num=secret_num, password=hashed_password)
        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return "Wrong Password"
    else:
        session_token = str(uuid.uuid4())
        user.session_token = session_token

        db.add(user)
        db.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

        return response


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

if __name__ == '__main__':
    app.run(port=5006)