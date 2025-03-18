from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    """
    Decorator to check if user is logged in
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function