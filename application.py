import sqlite3 
import os 
from flask import Flask

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True 

@app.route('/')
def hello_world():
    return 'Hello, World!'