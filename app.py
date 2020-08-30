import os

from datetime import date
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
# from cs50 import SQL
import psycopg2

from helpers import apology, login_required

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure database
DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
db = conn.cursor()

#db = SQL("sqlite:///reservations.db")
today = date.today()
# Clean up database -- clear out all time slots where date is less than today
db.execute("DELETE FROM slots WHERE date < :today", today=today)

@app.route("/pool", methods=["GET", "POST"])
def book_pool():
    #""" Book Pool"""
    id = session["user_id"]
    user_type = db.execute("SELECT type FROM users WHERE id=:id", id=id)
    if user_type[0]["type"] == "resident":
        if request.method=="GET":
            available_slots = db.execute("SELECT * FROM slots WHERE user_id IS NULL")
            return render_template("pool.html", slots=available_slots)
        
        elif request.method=="POST":
            slot_id = request.form.get("slot")
            db.execute("UPDATE slots SET user_id = :user_id WHERE slot_id = :slot_id", user_id=id, slot_id=slot_id)
        return render_template("reservation.html")
    else:
        return apology("Residents Only", 403)

@app.route("/reservation")
def reservation():
    #""" Reservations"""
    id = session["user_id"]
    user_type = db.execute("SELECT type FROM users WHERE id = :id", id=id)
    if user_type[0]["type"] == "resident":
        bookings = db.execute("SELECT * FROM slots WHERE user_id = :id", id=id)
        if not bookings:
            flash("You do not have any appointments!")
        return render_template("reservation.html", bookings=bookings)
    else:
        return apology("Must be a resident", 403)
        
@app.route("/cancel", methods=["GET","POST"])
def cancel():
    if request.method=="GET":
        return render_template("reservation.html")
    else:
        slot_id = request.form.get("cancel")
        db.execute("UPDATE slots SET user_id = NULL WHERE slot_id=:slot_id", slot_id=slot_id)
        flash("Reservation cancelled!")
        return render_template("reservation.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    id = session["user_id"]
    if request.method=="GET":
        user_type = db.execute("SELECT type FROM users WHERE id = :id", id=id)
        slots = db.execute("SELECT * FROM slots s LEFT JOIN residents r WHERE s.user_id = r.user_id")
        available_slots = db.execute("SELECT * FROM slots WHERE user_id IS NULL")
        if user_type[0]["type"] == "admin":
            return render_template("admin.html", slots=slots, available_slots=available_slots, today=today)
        else:
            return apology("Must be admin", 403)
    elif request.method=="POST":
        date = request.form.get("date")
        timeslot = request.form.get("timeslot")

        db.execute("INSERT INTO slots (date, time) VALUES (:date, :timeslot)", date=date, timeslot=timeslot)
        flash("New timeslot created!")
        return render_template("admin.html")

@app.route("/")
def index():
    #""" Setup homepage """
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    elif request.method=="POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        type = request.form.get("type")
        unit = request.form.get("unit")
        usernames = db.execute("SELECT username FROM users")

        if username in usernames:
            return apology("Username already exists", 403)
        elif username == "":
            return apology("Username cannot be blank", 403)
        elif password == "":
            return apology("Password cannot be blank", 403)
        elif password != confirmation:
            return apology("Passwords much match", 403)
        else:
            db.execute("INSERT INTO users (username, hash, type) VALUES (:username, :hash, :type)", username=username, hash=generate_password_hash(password), type=type)

        if type == "resident":
            id = db.execute("SELECT id FROM users WHERE username = :username", username=username)
            db.execute("INSERT INTO residents (user_id, unit) VALUES (:user_id, :unit)", user_id=id[0]["id"], unit=unit)
        flash("Registered")
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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

@app.route("/changepw", methods=["GET", "POST"])
def changepw():
    if request.method == "GET":
        return render_template("changepw.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")
        userid = db.execute("SELECT id FROM users WHERE username=:username", username=username)

        if not userid:
            return render_template("/register.html")
        elif username == "":
            return apology("Username cannot be blank", 403)
        elif password == "":
            return apology("Password cannot be blank", 403)
        elif password != confirm:
            return apology("Passwords much match", 403)
        # Update password in users table
        else:
            db.execute("UPDATE users SET hash=:hash WHERE id=:userid", hash=generate_password_hash(password), userid=userid[0]["id"])

        return render_template("/login.html")