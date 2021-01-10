import os 
import json
from datetime import datetime
from helpers import login_required, is_float, is_valid_email
from flask import Flask,  flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from models import User, Subscription, db, Recurrence
from werkzeug.security import check_password_hash, generate_password_hash

with open('./static/services.json') as f:
  services_file = json.load(f)

recurrences = [r.name for r in Recurrence]
services = services_file["services"]


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


# GET /subscription/1         -> get_subscription
# POST /subscription/1/update -> delete_subscription
# POST /subscription/1/delete -> delete_subscription

@app.route('/subscription/<id>', methods = ['GET'])
@login_required
def get_subscription(id):
    subscription = Subscription.query.filter_by(id=id, user_id=session['user_id']).first()
    if not subscription:
        return render_template('404.html')

    sub = {
        'id': subscription.id,
        'service': subscription.service,
        'subscribed_on': subscription.subscribed_on,
        'recurrence': subscription.recurrence.name.lower(),
        'price': round(subscription.price, 2)
    }

    return render_template('subscription.html', subscription=sub, services=services, recurrences= recurrences)


@app.route('/subscription/<id>/update', methods = ['POST'])
@login_required
def update_subscription(id):
    subscription = Subscription.query.filter_by(id=id).first()
    if not subscription:
        return render_template('404.html')

    # Get data from form
    service = request.form.get('service')
    subscribed_on = request.form.get('subscribed_on')
    price = request.form.get('price')
    recurrence = request.form.get('recurrence')

    #Check if service and date are not empty
    error = None
    if not service or service == '' or service not in [s['icon'] for s in services]:
        error = 'invalid service'
    elif not subscribed_on or subscribed_on == '':
        error = 'Invalid Subscription On value'
    elif not price or not is_float(price) or float(price) <= 0:
        error = 'Invalid price'
    elif not recurrence or recurrence == '' or recurrence.lower() not in recurrences:
        error = 'Invalid recurrence'

    if error != None:
        return render_template("add_subscription.html", recurrences=recurrences, services=services, error=error)

    # Update current subscription
    price = round(float(price), 2)
    subscribed_on = datetime.strptime(subscribed_on, '%Y-%m-%d')
    recurrence = recurrence.lower()

    subscription.service = service
    subscription.subscribed_on = subscribed_on
    subscription.price = price
    subscription.recurrence = recurrence

    db.session.commit()
    
    flash('Subscription updated!')
    return redirect('/home')

@app.route('/subscription/<id>/delete', methods = ['POST'])
@login_required
def delete_subscription(id):
    subscription = Subscription.query.filter_by(id=id).first()
    if not subscription:
        return render_template('404.html')

    db.session.delete(subscription)
    db.session.commit()
    
    flash('Subscription deleted!')
    return redirect('/home')
        

@app.route('/home')
@login_required
def home():
    subscriptions = Subscription.query.filter_by(user_id = session["user_id"]).all()
    subs = []
    for subscription in subscriptions:
        subs.append({
            'id': subscription.id,
            'price': round(subscription.price, 2),
            'recurrence': subscription.recurrence.name,
            'service': subscription.service
        })
    return render_template('home.html', subscriptions=subs)

@app.route('/login', methods=["GET", "POST"])
def login():
    '''Log user In'''
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        error = None
        if not email:
            error = 'Missing email'
        elif not password:
            error = 'Missing password'
        
        if error != None:
            return render_template("login.html", error=error)


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

        error = None
        if not email or not is_valid_email(email):
            error = 'Missing or invalid email'
        elif not password:
            error = 'Missing password'
        elif not confirmation or confirmation == '':
            error = 'Missing password confirmation'
        elif confirmation != password:
            error = 'Password and password confirmation do not match'
        
        if error != None:
            return render_template("register.html", error=error)

        # Ensure email isn't already taken
        num = User.query.filter_by(email=email).count()
        if num > 0:
            return "Email already taken"

        # Create new user
        new_user = User(full_name=full_name, email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        # Redirect user to login page
        return redirect("/login")

@app.route('/add-subscription', methods=["GET", "POST"])
@login_required
def add_subscription():
    if request.method == 'GET':
        return render_template("add_subscription.html", recurrences=recurrences, services=services)

    if request.method == 'POST':
        # Add subsciption to database
        service = request.form.get('service')
        subscribed_on = request.form.get('subscribed_on')
        price = request.form.get('price')
        recurrence = request.form.get('recurrence')

        #Check if service and date are not empty
        error = None
        if not service or service == '' or service not in [s['icon'] for s in services]:
            error = 'invalid service'
        elif not subscribed_on or subscribed_on == '':
            error = 'Invalid Subscription On value'
        elif not price or not is_float(price) or float(price) <= 0:
            error = 'Invalid price'
        elif not recurrence or recurrence == '' or recurrence.lower() not in recurrences:
            error = 'Invalid recurrence'

        if error != None:
            return render_template("add_subscription.html", recurrences=recurrences, services=services, error=error)

        # Create new subscription
        price = round(float(price), 2)
        subscribed_on = datetime.strptime(subscribed_on, '%Y-%m-%d')
        recurrence = recurrence.lower()

        new_subscription = Subscription(service=service, 
            subscribed_on=subscribed_on,
            price=price, 
            recurrence=recurrence,
            user_id=session["user_id"])

        db.session.add(new_subscription)
        db.session.commit()
    
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