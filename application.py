import os 
from flask import Flask,  flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from models import User, db
from werkzeug.security import check_password_hash, generate_password_hash


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
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    '''Log user In'''
    # Forget any user_id
    session.clear()

    email = request.form.get("email")
    password = request.form.get("password")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not email:
            return "must provide an email"

        # Ensure password was submitted
        elif not password:
            return "must provide password"

        # Query database for username
        user = User.query.filter_by(email=email)

    #     # Ensure username exists and password is correct
    #     if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
    #         return apology("invalid username and/or password", 403)

    #     # Remember which user has logged in
    #     session["user_id"] = rows[0]["id"]

    #     # Redirect user to home page
    #     return redirect("/")

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
        new_user = User(full_name= full_name, email=email, password=generate_password_hash(password))
        print(new_user)
        db.session.add(new_user)
        db.session.commit()

        # Redirect user to login page
        return redirect("/login")


@app.route("/logout")
def logout():
    '''Log user out'''

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



# @app.route('/get')
# def get():
#     users = User.query.all()
#     return {
#         'users': [{'id':u.id, 'full_name': u.full_name, 'email': u.email} for u in users]
#     }

# @app.route('/getone')
# def getone():
#     u = User.query.filter_by(full_name='azouz').first()
#     return render_template("user.html", user=u)

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)