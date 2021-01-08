import os 
import json
from datetime import datetime
from helpers import login_required
from flask import Flask,  flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from models import User, Subscription, db
from werkzeug.security import check_password_hash, generate_password_hash

with open('./static/services.json') as f:
  services_file = json.load(f)

# Configure application
app = Flask(__name__)

# Setup database with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subman.db'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    '''Log user In'''
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure email was submitted
        if not email:
            return "must provide an email"

        # Ensure password was submitted
        elif not password:
            return "must provide password"

        # Query database for email
        user = User.query.filter_by(email=email).first()

        # Ensure email exists and password is correct
        if not user or not check_password_hash(user.password, password):
            return "invalid email and/or password"

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("home")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route('/register' , methods=["GET", "POST"])
def register():
    '''Register User'''
    
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate email
        if not email or email == '':
            return "Must provide email"

        # Validate password
        if not password or password == '':
            return "Must provide password"

        # Validate password confirmation
        if not confirmation or confirmation == '':
            return "Must provide password confirmation"
        
        # Ensure password and password confirmation match
        if confirmation != password:
            return "Password and confirmation do not match"

        # Ensure email isn't already taken
        num = User.query.filter_by(email=email).count()
        print(num)
        if num > 0:
            return "Email already taken"

        # Create new user
        new_user = User(full_name=full_name, email=email, password=generate_password_hash(password))
        print(new_user)
        db.session.add(new_user)
        db.session.commit()

        # Redirect user to login page
        return redirect("/login")


@app.route('/test')
def test():
    date_time_str = '01/07/2021'
    date_time_obj = datetime.strptime(date_time_str, '%m/%d/%Y')

    new_subscription = Subscription(service='netflix', subscribed_on=date_time_obj, price='12',  recurrence='monthly', user_id=1)
    db.session.add(new_subscription)
    db.session.commit()

    print(new_subscription)
    return 'test'

@app.route('/add-subscription', methods=["GET", "POST"])
@login_required
def add_subscription():

    recurrences = ['Weekly', 'Monthly', 'Yearly']
    services = services_file["services"]

    if request.method == 'GET':
        return render_template("add_subscription.html", recurrences=recurrences, services=services)

    if request.method == 'POST':
        # Add subsciption to database
        service = request.form.get('service')
        subscribed_on = request.form.get('subscribed_on')
        price = request.form.get('price')
        recurrence = request.form.get('recurrence')

        error = None
        
        if not service or service == '':
            error = 'invalid service'
        elif not subscribed_on or subscribed_on == '':
            error = 'Invalid Subscription On value'

        if error != None:
            return render_template("add_subscription.html", recurrences=recurrences, services=services, error=error)

        # Create new subscription
        new_subscription = Subscription(service=service, 
            subscribed_on=subscribed_on,
            price=price, 
            recurrence=recurrence,
            user_id=session["user_id"])

        print(new_subscription)
        db.session.add(new_subscription)
        db.session.commit()
    
        # Redirect user to login page
        return redirect("/home")


@app.route("/logout")
def logout():
    '''Log user out'''

    # Forget any user_id
    session.clear()

    # Redirect user to index page
    return redirect("/")


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)