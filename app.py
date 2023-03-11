import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, has_int_and_upper

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

        name = request.form.get("username")
        passw = request.form.get("password")
    
        # Ensure username was submitted
        if not name:
            return render_template("login.html", err1=True)
        
        # Ensure password was submitted
        if not passw:
            return render_template("login.html", err2=True)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", name)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], passw):
            return render_template("login.html", err3=True)

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

    # Forget all session variables
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        name = request.form.get("username")
        passw = request.form.get("password")
        conf = request.form.get("confirmation")
    
        # Ensure username was submitted
        if not name:
            return render_template("register.html", err1=True)

        # Ensure password was submitted
        elif not passw or not conf:
            return render_template("register.html", err2=True)

        # Ensure passwords match
        elif passw != conf:
            return render_template("register.html", err3=True)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", name)

        # Ensure username doesn't exist
        if len(rows) != 0:
            return render_template("register.html", err4=True)

        # Ensure username is at least 3 characters long
        if len(name) < 4:
            return render_template("register.html", err5=True)
        
        # Ensure password format is right
        if len(passw) < 6 or not has_int_and_upper(passw):
            return render_template("register.html", err6=True)
            
        # Insert username and password information into sql database
        db.execute("INSERT INTO users (name, hash) VALUES(?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Update rows by querying after insertion
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["hp"] = rows[0]["hp"]

        session["playing"] = 0
        session["dealer"] = 0
        session["admin"] = 0
        session["dealers"] = [4, 5, 6, 7, 8, 9]

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
        id = int(request.form['user_id'])

        #initialize rows with user data
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # making sure user has enough hp
        if rows[0]["hp"] < 1:
            return jsonify({'success': False})
        
        # minus users hp and add dealers hp
        db.execute("UPDATE users SET hp = hp - 1, lucky = lucky + 1 WHERE id = ?", session["user_id"])
        db.execute("UPDATE users SET hp = hp + 1 WHERE id = ?", id)

        session["hp"] = rows[0]["hp"]
        hp = session["hp"]

        return jsonify({'success': True, 'hp': hp})
    else:
        return render_template("dealers.html")

@app.route("/players", methods=["GET", "POST"])
@login_required
def players():
    if request.method == "POST":
        id = int(request.form['user_id'])

        #initialize rows with user data
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # making sure user has enough hp
        if rows[0]["hp"] < 10:
            return jsonify({'success': False})
        
        # minus users hp and add dealers hp
        db.execute("UPDATE users SET hp = hp - 10, lucky = lucky + 10 WHERE id = ?", session["user_id"])
        db.execute("UPDATE users SET bounty = bounty + 1 WHERE id = ?", id)

        session["hp"] = rows[0]["hp"]
        hp = session["hp"]

        return jsonify({'success': True, 'hp': hp})
    else:
        players = db.execute("SELECT * FROM users ORDER BY hp")
        # add OFFSET int for skipping first few users^
        
        return render_template("players.html", players=players)

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