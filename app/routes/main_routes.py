from app.models.user import User
from flask import Blueprint, jsonify, render_template, session, redirect, url_for, request, flash, abort
from app.models.password import Password, PasswordShare
from app.services.password_service import generate_random_password, encrypt_password, decrypt_password
from app import db
from datetime import datetime

bp = Blueprint('main', __name__, url_prefix='')


@bp.route('/', methods=['GET'])
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    
    return render_template('index.html')


@bp.route('/dashboard', methods=['GET'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_passwords = Password.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('dashboard/index.html', passwords=user_passwords)


@bp.route('/password/generator', methods=['GET', 'POST'])
def password_generator():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    generated_password = None
    
    if request.method == 'POST':
        length = int(request.form.get('length', 16))
        include_uppercase = 'uppercase' in request.form
        include_digits = 'digits' in request.form
        include_special = 'special' in request.form
        
        generated_password = generate_random_password(
            length=length,
            include_uppercase=include_uppercase,
            include_digits=include_digits,
            include_special=include_special
        )
    
    return render_template('dashboard/generator.html', generated_password=generated_password)


@bp.route('/password/store-generated', methods=['POST'])
def store_generated_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    generated_password = request.form.get('generated_password')
    if generated_password:
        session['generated_password'] = generated_password
    
    return redirect(url_for('main.add_password'))


@bp.route('/password/add', methods=['GET', 'POST'])
def add_password():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    generated_password = session.pop('generated_password', None)
    
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not site_name or not password:
            flash('Le nom du site et le mot de passe sont obligatoires', 'error')
            return render_template('dashboard/add_password.html', generated_password=generated_password)
        
        user = User.query.get(session['user_id'])
        
        encrypted_password, encryption_iv = encrypt_password(
            password, 
            user.id, 
            user.encryption_salt
        )
        
        new_password = Password(
            user_id=session['user_id'],
            site_name=site_name,
            username=username,
            encrypted_password=encrypted_password,
            encryption_iv=encryption_iv
        )
        
        db.session.add(new_password)
        db.session.commit()
        
        flash('Mot de passe ajouté avec succès!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('dashboard/add_password.html', generated_password=generated_password)


@bp.route('/password/<int:password_id>/view', methods=['GET'])
def view_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    password_entry = Password.query.filter_by(id=password_id, user_id=session['user_id']).first_or_404()
    user = User.query.get(session['user_id'])
    
    decrypted_password = decrypt_password(
        password_entry.encrypted_password,
        password_entry.encryption_iv,
        user.id,
        user.encryption_salt
    )
    
    return render_template('dashboard/view_password.html', password=password_entry, decrypted_password=decrypted_password)


@bp.route('/password/<int:password_id>/delete', methods=['POST'])
def delete_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    password_entry = Password.query.filter_by(id=password_id, user_id=session['user_id']).first_or_404()
    
    db.session.delete(password_entry)
    db.session.commit()
    
    flash('Mot de passe supprimé avec succès!', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/password/<int:password_id>/share', methods=['GET', 'POST'])
def share_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    password_entry = Password.query.filter_by(id=password_id, user_id=session['user_id']).first_or_404()
    
    active_shares = [share for share in password_entry.shares if not share.is_expired()]
    
    if request.method == 'POST':
        expiration_hours = int(request.form.get('expiration_hours', 24))
        
        share = PasswordShare.create_share(password_id, expiration_hours)
        
        share_url = url_for('main.access_shared_password', token=share.share_token, _external=True)
        
        return render_template('dashboard/share_password.html', 
                              password=password_entry, 
                              active_shares=active_shares,
                              new_share=share,
                              share_url=share_url)
    
    return render_template('dashboard/share_password.html', 
                          password=password_entry, 
                          active_shares=active_shares)


@bp.route('/password/share/<token>', methods=['GET'])
def access_shared_password(token):
    share = PasswordShare.get_by_token(token)
    
    if not share:
        abort(404)  
    
    password_entry = Password.query.get_or_404(share.password_id)
    
    owner_user = User.query.get(password_entry.user_id)
    
    decrypted_password = decrypt_password(
        password_entry.encrypted_password,
        password_entry.encryption_iv,
        owner_user.id,          
        owner_user.encryption_salt  
    )
    
    remaining_time = share.expires_at - datetime.utcnow()
    remaining_hours = remaining_time.total_seconds() // 3600
    remaining_minutes = (remaining_time.total_seconds() % 3600) // 60
    
    return render_template('shared_password.html', 
                          password=password_entry,
                          decrypted_password=decrypted_password,
                          remaining_hours=int(remaining_hours),
                          remaining_minutes=int(remaining_minutes))


@bp.route('/password/share/<token>/delete', methods=['POST'])
def delete_share(token):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    share = PasswordShare.query.filter_by(share_token=token).first_or_404()
    
    password_entry = Password.query.get_or_404(share.password_id)
    if password_entry.user_id != session['user_id']:
        abort(403)
    
    db.session.delete(share)
    db.session.commit()
    
    flash('Partage supprimé avec succès!', 'success')
    return redirect(url_for('main.share_password', password_id=password_entry.id))