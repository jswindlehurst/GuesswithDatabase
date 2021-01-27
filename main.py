from flask import Flask, render_template, request, redirect, url_for, make_response
from model import User, db
import random

app = Flask(__name__)
db.create_all()


@app.route("/")
def index():


    return render_template("index.html")

@app.route("/guessing")
def guessing():

    return render_template("guessing.html")


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("user-name")
    email = request.form.get("user-email")
    secret_num = random.randint(1, 50)

    user = User(name=name, email=email, secret_num=secret_num)

    db.add(user)
    db.commit()

    response = make_response(redirect(url_for('index')))
    response.set_cookie("secret_num", str(secret_num))

    return response


@app.route("/guess", methods=["POST"])
def guess():

    secret_num = int(request.cookies.get("secret_num"))
    guess = int(request.form.get("your-guess"))

    if not guess:
        return "Please choose a number between 1 - 50"

    elif guess == secret_num:
        return "Success.  You guessed correctly"
    elif guess < secret_num:
        return "Try a bigger number"
    else:
        return "Try a smaller number"

    response = make_response(render_template("results.html"))
    return response


    return response

if __name__ == '__main__':
    app.run(port=5003)