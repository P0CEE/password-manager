from flask import Blueprint, jsonify, render_template

bp = Blueprint('main', __name__, url_prefix='')

@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({"status": "online", "message": "Password Manager API is running"})