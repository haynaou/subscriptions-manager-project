import os 
from flask import Flask,  flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from tempfile import mkdtemp
from models import User, db

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

@app.route('/create')
def create():
    user = User(full_name='bb', email='ll', password= 'kk' )
    db.session.add(user)
    db.session.commit()
    return 'Created user'

@app.route('/get')
def get():
    users = User.query.all()
    return {
        'users': [{'id':u.id, 'full_name': u.full_name, 'email': u.email} for u in users]
    }

@app.route('/getone')
def getone():
    u = User.query.filter_by(full_name='azouz').first()
    return render_template("user.html", user=u)

if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)