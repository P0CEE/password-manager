from flask import Blueprint, jsonify, render_template, session, redirect, url_for

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
    
    return render_template('dashboard/index.html')