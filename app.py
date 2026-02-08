from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = "simple_secret_key"

# email format check
EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


# db connection
def connect_db():
    return sqlite3.connect("database.db")


# creating users table
def init_db():
    db = connect_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    db.commit()


init_db()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        # email check
        if not re.match(EMAIL_PATTERN, email):
            return "Invalid email format"

        db = connect_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        # user not found
        if user is None:
            return "User not found"

        # password check
        if not check_password_hash(user[2], password):
            return "Wrong password"

        # session start
        session["user_id"] = user[0]
        session["email"] = user[1]

        print("login:", email)

        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        # email check
        if not re.match(EMAIL_PATTERN, email):
            return "Invalid email format"

        if len(password) < 8:
            return "Password too short"

        hashed_password = generate_password_hash(password)

        db = connect_db()
        try:
            db.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed_password)
            )
            db.commit()
            return redirect("/")
        except sqlite3.IntegrityError:
            return "Email already exists"

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    # allow only logged in users
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    # clear session
    session.clear()
    print("logout done")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
