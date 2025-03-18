from flask import Blueprint, request, render_template, redirect, url_for, session
from app import db
from app.models.user import User
from app.services.password_service import generate_password
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            error = "Email inconnu. Veuillez vérifier votre email ou créer un compte."
        elif not check_password_hash(user.password, password):
            error = "Mot de passe incorrect. Veuillez réessayer."
        else:
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.dashboard'))
            
    return render_template('index.html', error=error)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            error = "Les mots de passe ne correspondent pas."
        elif len(password) < 8:
            error = "Le mot de passe doit contenir au moins 8 caractères."
        else:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                error = "Cet email est déjà utilisé. Veuillez en choisir un autre."
            else:
                existing_username = User.query.filter_by(username=username).first()
                if existing_username:
                    error = "Ce nom d'utilisateur est déjà utilisé. Veuillez en choisir un autre."
        
        if error is None:
            password_hash = generate_password(password)
            new_user = User(username=username, email=email, password=password_hash)
            
            try:
                db.session.add(new_user)
                db.session.commit()
                
                session['user_id'] = new_user.id
                session['username'] = new_user.username
                
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                db.session.rollback()
                error = f"Une erreur est survenue: {str(e)}"
    
    return render_template('auth/register.html', error=error)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))