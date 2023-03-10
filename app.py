import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")

# app.secret_key = "27eduCBA09"

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # # Ensure username was submitted
        # if not request.form.get("username"):
        #     return apology("must provide username", 403)

        # # Ensure password was submitted
        # elif not request.form.get("password"):
        #     return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))

        # # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #     return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["hp"] = rows[0]["hp"]

        session["playing"] = 0
        session["dealer"] = 0
        session["admin"] = 0
        session["dealers"] = [3, 4, 5, 6, 7, 8, 9]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # # Ensure username was submitted
        # if not request.form.get("username"):
        #     return apology("must provide username", 400)

        # # Ensure password was submitted
        # elif not request.form.get("password"):
        #     return apology("must provide password", 400)

        # # Ensure passwords match
        # elif request.form.get("password") != request.form.get("confirmation"):
        #     return apology("passwords don't match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("name"))

        # # Ensure username doesn't exist
        # if len(rows) != 0:
        #     return apology("username already exists", 400)

        # Insert username and password information into sql database
        db.execute("INSERT INTO users (name, hash) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Update rows by querying after insertion
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["hp"] = 0

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/rules")
@login_required
def rules():
    return render_template("rules.html")

@app.route("/dealers", methods=["GET", "POST"])
@login_required
def dealers():
    if request.method == "POST":
        tip = int(request.form.get("tip"))
        id = int(request.form.get("id"))

        #initialize rows with user data
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # unimplemented error checking
        # if rows[0]["hp"] < tip:
        #     return apology("not enough hp balance", 400)

        # minus users hp and add dealers hp
        db.execute("UPDATE users SET hp = hp - ? WHERE id = ?", tip, session["user_id"])
        db.execute("UPDATE users SET hp = hp + ? WHERE id = ?", tip, id)

        session["hp"] = rows[0]["hp"]

        return redirect("/dealers")
    else:
        return render_template("dealers.html")

@app.route("/leaderboard")
@login_required
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/tables", methods=["GET", "POST"])
@login_required
def tables():
    return render_template("tables.html")

@app.route("/table1", methods=["GET", "POST"])
@login_required
def table1():
    return render_template("table1.html")

@app.route("/table2", methods=["GET", "POST"])
@login_required
def table2():
    return render_template("table2.html")

@app.route("/table3", methods=["GET", "POST"])
@login_required
def table3():
    return render_template("table3.html")

@app.route("/table4", methods=["GET", "POST"])
@login_required
def table4():
    return render_template("table4.html")

@app.route("/table5", methods=["GET", "POST"])
@login_required
def table5():
    return render_template("table5.html")

@app.route("/table6", methods=["GET", "POST"])
@login_required
def table6():
    return render_template("table6.html")

@app.route("/table7", methods=["GET", "POST"])
@login_required
def table7():
    return render_template("table7.html")

@app.route("/table8", methods=["GET", "POST"])
@login_required
def table8():
    return render_template("table8.html")