import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from fractions import Fraction
import random

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
def start():
    return render_template("start.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/admin", methods=["GET", "POST"])
@login_required 
def admin():
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        bounty = request.form.get("bounty")
        hp = request.form.get("hp")
        updateid = request.form.get("updateid")
        id = request.form.get("id")
        idplay = request.form.get("idplay")
        convert = request.form.get("convert")
        
        if bounty:
            db.execute("UPDATE users SET bounty = ? WHERE id = ?", bounty, updateid)
            
        if hp:
            db.execute("UPDATE users SET hp = ? WHERE id = ?", hp, updateid)
        
        if id:
            db.execute("UPDATE users SET playing = 0 WHERE id = ?", id)   
            
        if idplay:
            db.execute("UPDATE users SET playing = 1, hp = hp + 10 WHERE id = ?", idplay)   
            
        if convert:
            users = db.execute("SELECT * FROM users")
            for user in users:
                bountyhp = user["bounty"] * 10
                db.execute("UPDATE users SET  hp = hp + ?, bounty = bounty - ? WHERE id = ?", bountyhp, user["bounty"], user["id"])
                db.execute("UPDATE users SET lucky = lucky + ?, hp = hp - ? WHERE id = ?", user["hp"], user["hp"], user["id"])
        
        persons = db.execute("SELECT * FROM users")
        
        return render_template("admin.html", persons=persons)
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        persons = db.execute("SELECT * FROM users")
        
        return render_template("admin.html", persons=persons)

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

        session["playing"] = rows[0]["playing"]
        session["dealer"] = rows[0]["dealing"]
        session["admin"] = rows[0]["permission"]
        session["dealers"] = [4, 5, 6, 7, 8, 9, 10]
        
        # consider putting this into another route to make process faster so regulars dont need this code?
        tablerow = db.execute("SELECT * FROM tables")
        for i in range(len(tablerow)):
            if tablerow[i]["dealerid"] > 1:
                session["occupied" + str(i + 1)] = True
            session["dealerid" + str(i + 1)] = tablerow[i]["dealerid"]
                
        # Redirect user to home page
        return redirect("/home")

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
        email = request.form.get("email")
    
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

        if email:
            db.execute("UPDATE users SET email = ? WHERE name = ?", email, name)
        
        # Update rows by querying after insertion
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["hp"] = rows[0]["hp"]

        session["playing"] = rows[0]["playing"]
        session["dealer"] = rows[0]["dealing"]
        session["admin"] = rows[0]["permission"]
        session["dealers"] = [4, 5, 6, 7, 8, 9, 10]

        # Redirect user to home page
        return redirect("/home")

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

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        
        session["hp"] = rows[0]["hp"]
        hp = session["hp"]

        return jsonify({'success': True, 'hp': hp})
    else:
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
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

        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        session["hp"] = rows[0]["hp"]
        hp = session["hp"]

        return jsonify({'success': True, 'hp': hp})
    else:
        players = db.execute("SELECT * FROM users ORDER BY hp")
        # add OFFSET int for skipping first few users^
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("players.html", players=players)

@app.route("/leaderboard")
@login_required
def leaderboard():
    players = db.execute("SELECT * FROM users ORDER BY bounty ")
        # add OFFSET int for skipping first few users^
    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
    session["hp"] = rows[0]["hp"]
    return render_template("leaderboard.html", players=players)

@app.route("/lottery", methods=["GET", "POST"])
@login_required
def lottery():
    if request.method == "POST":
        lst = []
        persons = db.execute("SELECT * FROM users")
        for person in persons:
            luckys = int(person["lucky"])
            for i in range(luckys):
                lst.append(person["name"])
        num = random.randrange(1, len(lst))
        winner = lst[num]
        return render_template("lottery.html", winner=winner)
    else:
        return render_template("lottery.html")

@app.route("/tables", methods=["GET", "POST"])
@login_required
def tables():
    if request.method == "POST":
        tableid = int(request.form.get("tableid"))
        if tableid == 1:
            return redirect("/table1")
        if tableid == 2:
            return redirect("/table2")
        if tableid == 3:
            return redirect("/table3")
        if tableid == 4:
            return redirect("/table4")
        if tableid == 5:
            return redirect("/table5")
        if tableid == 6:
            return redirect("/table6")
        if tableid == 7:
            return redirect("/table7")
        if tableid == 8:
            return redirect("/blackjacktable")
        if tableid == 9:
            return redirect("/acetable")
        
        return redirect("/tables")
    else:
        tables = db.execute("SELECT * FROM tables")
        return render_template("tables.html", tables=tables)

@app.route("/myTable", methods=["GET"])
@login_required
def mytable():
    if session["dealerid1"] == session["user_id"]:
        return redirect("/table1")
    if session["dealerid2"] == session["user_id"]:
        return redirect("/table2")
    if session["dealerid3"] == session["user_id"]:
        return redirect("/table3")
    if session["dealerid4"] == session["user_id"]:
        return redirect("/table4")
    if session["dealerid5"] == session["user_id"]:
        return redirect("/table5")
    if session["dealerid6"] == session["user_id"]:
        return redirect("/table6")
    if session["dealerid7"] == session["user_id"]:
        return redirect("/table7")
    if session["dealerid8"] == session["user_id"]:
        return redirect("/blackjacktable")
    if session["dealerid9"] == session["user_id"]:
        return redirect("/acetable")
    
    return redirect("/tables")
    
@app.route("/addplayer", methods=["POST"])
@login_required
def addplayer():
    id = request.form.get("addid")
    tableid = request.form.get("tableid")
    db.execute("UPDATE users SET poker = ? WHERE id = ?", tableid, id)
    db.execute("UPDATE users SET tableid = ? WHERE id = ?", tableid, id)
    return redirect("/myTable")

@app.route("/table1", methods=["GET", "POST"])
@login_required
def table1():
    if request.method == "POST":
        # this part deals with checking in the dealer
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 1", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 1")
            session["occupied1"] = True
            session["dealerid1"] = row[0]["dealerid"]

        players = db.execute("SELECT * FROM users WHERE poker = 1")
        persons = db.execute("SELECT * FROM users WHERE playing = 1")
        
        # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table1.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 1")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied1"] = True
        session["dealerid1"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 1")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table1.html", dealer=dealer, players=players, persons=persons)

@app.route("/table2", methods=["GET", "POST"])
@login_required
def table2():
    if request.method == "POST":
        # this part deals with checking in the dealer
        # keep in mind the int is because request.form.get returns a string, which messes up the comparison in jinja
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 2", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 2")
            session["occupied2"] = True
            session["dealerid2"] = row[0]["dealerid"]
        
        players = db.execute("SELECT * FROM users WHERE poker = 2")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
         # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table2.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 2")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied2"] = True
        session["dealerid2"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 2")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table2.html", dealer=dealer, players=players, persons=persons)

@app.route("/table3", methods=["GET", "POST"])
@login_required
def table3():
    if request.method == "POST":
        # this part deals with checking in the dealer
        # keep in mind the int is because request.form.get returns a string, which messes up the comparison in jinja
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 3", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 3")
            session["occupied3"] = True
            session["dealerid3"] = row[0]["dealerid"]
        
        players = db.execute("SELECT * FROM users WHERE poker = 3")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
         # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table3.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 3")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied3"] = True
        session["dealerid3"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 3")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table3.html", dealer=dealer, players=players, persons=persons)

@app.route("/table4", methods=["GET", "POST"])
@login_required
def table4():
    if request.method == "POST":
        # this part deals with checking in the dealer
        # keep in mind the int is because request.form.get returns a string, which messes up the comparison in jinja
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 4", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 4")
            session["occupied4"] = True
            session["dealerid4"] = row[0]["dealerid"]
        
        players = db.execute("SELECT * FROM users WHERE poker = 4")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
         # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table4.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 4")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied4"] = True
        session["dealerid4"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 4")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table4.html", dealer=dealer, players=players, persons=persons)

@app.route("/table5", methods=["GET", "POST"])
@login_required
def table5():
    if request.method == "POST":
        # this part deals with checking in the dealer
        # keep in mind the int is because request.form.get returns a string, which messes up the comparison in jinja
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 5", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 5")
            session["occupied5"] = True
            session["dealerid5"] = row[0]["dealerid"]
    
        players = db.execute("SELECT * FROM users WHERE poker = 5")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
         # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table5.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 5")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied5"] = True
        session["dealerid5"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 5")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table5.html", dealer=dealer, players=players, persons=persons)

@app.route("/table6", methods=["GET", "POST"])
@login_required
def table6():
    if request.method == "POST":
        # this part deals with checking in the dealer
        # keep in mind the int is because request.form.get returns a string, which messes up the comparison in jinja
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 6", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 6")
            session["occupied6"] = True
            session["dealerid6"] = row[0]["dealerid"]
        
        players = db.execute("SELECT * FROM users WHERE poker = 6")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
         # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table6.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 6")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied6"] = True
        session["dealerid6"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 6")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table6.html", dealer=dealer, players=players, persons=persons)

@app.route("/table7", methods=["GET", "POST"])
@login_required
def table7():
    if request.method == "POST":
        # this part deals with checking in the dealer
        # keep in mind the int is because request.form.get returns a string, which messes up the comparison in jinja
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 7", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 7")
            session["occupied7"] = True
            session["dealerid7"] = row[0]["dealerid"]
        
        players = db.execute("SELECT * FROM users WHERE poker = 7")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
         # this part checks for elimination
        eliminated = request.form.get("eliminated")
        if eliminated:
            return render_template("eliminate.html", players=players, eliminated=eliminated)
        
        return render_template("table7.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 7")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied7"] = True
        session["dealerid7"] = dealer
        players = db.execute("SELECT * FROM users WHERE poker = 7")
        persons = db.execute("SELECT * FROM users WHERE playing = 1 AND poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("table7.html", dealer=dealer, players=players, persons=persons)

@app.route("/eliminate", methods=["POST"])
@login_required
def eliminate():
    eliminated = request.form.get("eliminated")
    eliminator = request.form.getlist("eliminators[]")
    
    if len(eliminator) == 0:
        db.execute("UPDATE users SET poker = 0 WHERE id = ?", eliminated)
        return redirect("myTable")
    
    # make sure eliminator and eliminated isnt the same person
    if eliminated in eliminator:
        return redirect("myTable")
    
    rows = db.execute("SELECT * FROM users WHERE id = ?", eliminated)
    bounty = rows[0]["bounty"]
    
    if len(eliminator) > 1:
        eliminators = len(eliminator)
        bounty = bounty // eliminators
        for i in range(eliminators):
            db.execute("UPDATE users SET bounty = bounty + ? WHERE id = ?", bounty, eliminator[i])
        db.execute("UPDATE users SET bounty = 0, playing = 0, poker = 0 WHERE id = ?", eliminated)
        return redirect("myTable")
    
    db.execute("UPDATE users SET bounty = bounty + ? WHERE id = ?", bounty, eliminator[0])
    db.execute("UPDATE users SET bounty = 0, playing = 0, poker = 0  WHERE id = ?", eliminated)
    
    return redirect("/myTable")

@app.route("/checkout", methods=["POST"])
@login_required 
def checkout():
    id = request.form.get("checkoutid")
    tableid = db.execute("SELECT * FROM tables WHERE dealerid = ?", id)
    db.execute("UPDATE tables SET dealerid = 0 WHERE dealerid = ?", id)
    db.execute("UPDATE users SET poker = 0 WHERE tableid = ?", tableid[0]["id"])
    session["dealerid" + str(tableid[0]["id"])] = None
    session["occupied" + str(tableid[0]["id"])] = False
    return redirect("/myTable")

@app.route("/blackjack", methods=["GET", "POST"])
@login_required
def blackjack():
    if request.method == "POST":
        bet = request.form.get("bet")
        error = 0
        if not bet or isinstance(bet, Fraction) or not bet.isdigit() or not float(bet).is_integer() or float(bet) < 1:  
            error = 1
            return render_template("blackjack.html", status=status, playing=playing, error=error)
        playingstatus = db.execute("SELECT * FROM blackjackstatus")
        playing = playingstatus[0]["status"]
        status = 0
        users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if int(bet) <= users[0]["hp"]:
            db.execute("UPDATE blackjack SET bet = ? WHERE player = ?", bet, session["user_id"])
            session["blackjack"] = 2
            return render_template("blackjack.html", status=status, playing=playing, error=error)
        else:
            status = 0
            return render_template("blackjack.html", status=status, playing=playing, error=error)
    else:
        rows = db.execute("SELECT * FROM blackjack")
        error = 0
        playingstatus = db.execute("SELECT * FROM blackjackstatus")
        playing = playingstatus[0]["status"]
        status = 0
        
        ro = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = ro[0]["hp"]
        
        for row in rows:
            if row["player"] == session["user_id"]:
                status = 1
                return render_template("blackjack.html", status=status, playing=playing, error=error)
        return render_template("blackjack.html", status=status, playing=playing, error=error)
    
@app.route("/blackjacktable", methods=["GET", "POST"])
@login_required
def blackjacktable():
    if request.method == "POST":
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 8", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 8")
            session["occupied8"] = True
            session["dealerid8"] = row[0]["dealerid"]
        
        # players = db.execute("SELECT * FROM users WHERE poker = 8")
        players = db.execute("SELECT * FROM blackjack")
        persons = db.execute("SELECT * FROM users WHERE poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("blackjacktable.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 8")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied8"] = True
        session["dealerid8"] = dealer
        players = db.execute("SELECT * FROM blackjack")
        persons = db.execute("SELECT * FROM users WHERE poker = 0")
        
        row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = row[0]["hp"]
        
        return render_template("blackjacktable.html", dealer=dealer, players=players, persons=persons)
        
@app.route("/addplayerbj", methods=["POST"])
@login_required
def addplayerbj():
    id = request.form.get("addid")
    users = db.execute("SELECT * FROM users WHERE id = ?", id)
    db.execute("INSERT INTO blackjack (player, name) VALUES(?, ?)", id, users[0]["name"])
    db.execute("UPDATE users SET poker = 8 WHERE id = ?", id)
    db.execute("UPDATE users SET tableid = 8 WHERE id = ?", id)
    return redirect("/blackjacktable")

@app.route("/bjlogic", methods=["POST"])
@login_required
def bjlogic():
    winner = request.form.get("winner")
    loser = request.form.get("loser")
    tie = request.form.get("tie")
    x2 = request.form.get("x2")
    removeid = request.form.get("removeid")
    
    better = db.execute("SELECT * FROM blackjack WHERE player = ?", winner)
    if better:
        i = better[0]["bet"]
    if winner:
        db.execute("UPDATE users SET hp = hp + ? WHERE id = ?", i, winner)
        db.execute("UPDATE blackjack SET bet = 0 WHERE player = ?", winner)
        return redirect("/blackjacktable")

    better = db.execute("SELECT * FROM blackjack WHERE player = ?", loser)
    if better:
        i = better[0]["bet"]
    if loser:
        db.execute("UPDATE users SET hp = hp - ? WHERE id = ?", i, loser)
        db.execute("UPDATE blackjack SET bet = 0 WHERE player = ?", loser) 
        return redirect("/blackjacktable")
    
    if tie:
        db.execute("UPDATE blackjack SET bet = 0 WHERE player = ?", tie)
        return redirect("/blackjacktable")
    
    if x2:
        bet = db.execute("SELECT * FROM blackjack WHERE player = ?", x2)
        row = db.execute("SELECT * FROM users WHERE id = ?", x2)
        if int(bet[0]["bet"]) * 2 > int(row[0]["hp"]):
            return redirect("/blackjacktable")
        db.execute("UPDATE blackjack SET bet = bet * 2 WHERE id = ?", x2)
        
    if removeid:
        db.execute("DELETE FROM blackjack WHERE player = ?", removeid)
        db.execute("UPDATE users SET poker = 0 WHERE id = ?", removeid)
        db.execute("UPDATE users SET tableid = 0 WHERE id = ?", removeid)
        return redirect("/blackjacktable")
        
    return redirect("/blackjacktable")
        
@app.route("/playingstatus", methods=["POST"])
@login_required
def playingstatus():
    status = int(request.form.get("playing"))
    if status == 1:
        db.execute("UPDATE blackjackstatus SET status = 1")
        return redirect("/blackjacktable")
    else:
        db.execute("UPDATE blackjackstatus SET status = 0")
        return redirect("/blackjacktable")
    
@app.route("/bjcheckout", methods=["POST"])
@login_required 
def bjcheckout():
    id = request.form.get("checkoutid")
    tableid = db.execute("SELECT * FROM tables WHERE dealerid = ?", id)
    db.execute("UPDATE tables SET dealerid = 0 WHERE dealerid = ?", id)
    db.execute("UPDATE users SET poker = 0 WHERE tableid = ?", tableid[0]["id"])
    db.execute("UPDATE users SET tableid = 0 WHERE tableid = ?", tableid[0]["id"])
    db.execute("UPDATE blackjackstatus SET status = 0")
    db.execute("DELETE FROM blackjack")
    session["dealerid" + str(tableid[0]["id"])] = None
    session["occupied" + str(tableid[0]["id"])] = False
    return redirect("/myTable")

@app.route("/acerace", methods=["GET", "POST"])
@login_required 
def acerace():
    if request.method == "POST":
        choice = request.form.get("choice")
        bet = request.form.get("bet")
        error = 0
        if not bet or isinstance(bet, Fraction) or not bet.isdigit() or not float(bet).is_integer() or float(bet) < 1:  
            error = 1
            return render_template("acerace.html", status=status, playing=playing, error=error)
        playingstatus = db.execute("SELECT * FROM arstatus")
        playing = playingstatus[0]["status"]
        status = 0
        users = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        if int(bet) <= users[0]["hp"]:
            db.execute("UPDATE acerace SET bet = ? WHERE player = ?", bet, session["user_id"])
            db.execute("UPDATE acerace SET choice = ? WHERE player = ?", choice, session["user_id"])
            session["acerace"] = 2
            return render_template("acerace.html", status=status, playing=playing, error=error)
        else:
            status = 0
            return render_template("acerace.html", status=status, playing=playing, error=error)
    else:
        rows = db.execute("SELECT * FROM acerace")
        error = 0
        playingstatus = db.execute("SELECT * FROM arstatus")
        playing = playingstatus[0]["status"]
        status = 0
        
        ro = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = ro[0]["hp"]
        
        for row in rows:
            if row["player"] == session["user_id"]:
                status = 1
                return render_template("acerace.html", status=status, playing=playing, error=error)
        return render_template("acerace.html", status=status, playing=playing, error=error)
    
@app.route("/addplayerar", methods=["POST"])
@login_required 
def addplayerar():
    id = request.form.get("addid")
    users = db.execute("SELECT * FROM users WHERE id = ?", id)
    db.execute("INSERT INTO acerace (player, name) VALUES(?, ?)", id, users[0]["name"])
    db.execute("UPDATE users SET poker = 9 WHERE id = ?", id)
    db.execute("UPDATE users SET tableid = 9 WHERE id = ?", id)
    return redirect("/acetable")

@app.route("/arlogic", methods=["POST"])
@login_required 
def arlogic():
    diamond = request.form.get("diamond")
    club = request.form.get("club")
    heart = request.form.get("heart")
    spade = request.form.get("spade")
    removeid = request.form.get("removeid")
    
    if diamond:
        rows = db.execute("SELECT * FROM acerace")
        for row in rows:
            if int(row["choice"]) == int(diamond):
                better = db.execute("SELECT * FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp + ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
            else:
                better = db.execute("SELECT * FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                    db.execute("UPDATE users SET hp = hp - ? WHERE id = ?", i, row["player"])
                    db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
        return redirect("/acetable")
    
    if club:
        rows = db.execute("SELECT * FROM acerace")
        for row in rows:
            if int(row["choice"]) == int(club):
                better = db.execute("SELECT bet FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp + ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
            else:
                better = db.execute("SELECT bet FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp - ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
        return redirect("/acetable")
            
    if heart:
        rows = db.execute("SELECT * FROM acerace")
        for row in rows:
            if int(row["choice"]) == int(heart):
                better = db.execute("SELECT bet FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp + ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
            else:
                better = db.execute("SELECT bet FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp - ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
        return redirect("/acetable")
    
    if spade:
        rows = db.execute("SELECT * FROM acerace")
        for row in rows:
            if int(row["choice"]) == int(spade):
                better = db.execute("SELECT bet FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp + ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
            else:
                better = db.execute("SELECT bet FROM acerace WHERE player = ?", row["player"])
                if better:
                    i = better[0]["bet"]
                db.execute("UPDATE users SET hp = hp - ? WHERE id = ?", i, row["player"])
                db.execute("UPDATE acerace SET bet = 0, choice = 0 WHERE player = ?", row["player"])
        return redirect("/acetable")
    
    if removeid:
        db.execute("DELETE FROM acerace WHERE player = ?", removeid)
        db.execute("UPDATE users SET poker = 0 WHERE id = ?", removeid)
        db.execute("UPDATE users SET tableid = 0 WHERE id = ?", removeid)
        return redirect("/acetable")
    return redirect("/acetable")

@app.route("/acetable", methods=["GET", "POST"])
@login_required 
def acetable():
    if request.method == "POST":
        dealer = request.form.get("id")
        if dealer:
            db.execute("UPDATE tables SET dealerid = ? WHERE id = 9", dealer)
            row = db.execute("SELECT * FROM tables WHERE id = 9")
            session["occupied9"] = True
            session["dealerid9"] = row[0]["dealerid"]
        
        # players = db.execute("SELECT * FROM users WHERE poker = 9")
        players = db.execute("SELECT * FROM acerace")
        persons = db.execute("SELECT * FROM users WHERE poker = 0")
        
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = rows[0]["hp"]
        
        return render_template("acetable.html", dealer=dealer, players=players, persons=persons)
    else:
        rows = db.execute("SELECT * FROM tables WHERE id = 9")
        dealer = rows[0]["dealerid"]
        if dealer == session["user_id"]:
            session["occupied9"] = True
        session["dealerid9"] = dealer
        players = db.execute("SELECT * FROM acerace")
        persons = db.execute("SELECT * FROM users WHERE poker = 0")
        
        row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        session["hp"] = row[0]["hp"]
        
        return render_template("acetable.html", dealer=dealer, players=players, persons=persons)

@app.route("/archeckout", methods=["POST"])
@login_required 
def archeckout():
    id = request.form.get("checkoutid")
    tableid = db.execute("SELECT * FROM tables WHERE dealerid = ?", id)
    db.execute("UPDATE tables SET dealerid = 0 WHERE dealerid = ?", id)
    db.execute("UPDATE users SET poker = 0 WHERE tableid = ?", tableid[0]["id"])
    db.execute("UPDATE users SET tableid = 0 WHERE tableid = ?", tableid[0]["id"])
    db.execute("UPDATE arstatus SET status = 0")
    db.execute("DELETE FROM acerace")
    session["dealerid" + str(tableid[0]["id"])] = None
    session["occupied" + str(tableid[0]["id"])] = False
    return redirect("/myTable")

@app.route("/playingstatusar", methods=["POST"])
@login_required 
def playingstatusar():
    status = int(request.form.get("playing"))
    if status == 1:
        db.execute("UPDATE arstatus SET status = 1")
        return redirect("/acetable")
    else:
        db.execute("UPDATE arstatus SET status = 0")
        return redirect("/acetable")


    

    
