from functools import wraps
from flask import redirect, session
import re 

# error message
# Delete/modify subscriptions

# login required 
def login_required(f):
    """
    Decorate routes to require login.
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
    
# Check if variable is float
def is_float(var):
  try:
      float(var)
      return True
  except ValueError:
      return False


# Define a function for validating an Email 
def is_valid_email(email):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if (re.search(regex, email)):  
        return True
    return False
