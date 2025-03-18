from flask import Blueprint, jsonify

bp = Blueprint('main', __name__, url_prefix='')

@bp.route('/', methods=['GET'])
def index():
    return jsonify({"status": "online", "message": "Password Manager API is running"})