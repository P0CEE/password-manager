from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.password import Password
from app.services.password_service import generate_password, check_password

bp = Blueprint('user_routes', __name__, url_prefix='/users')

@bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']

    password_hash = generate_password(password)

    new_user = User(username=username, email=email, password=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

@bp.route('/<int:user_id>/passwords', methods=['POST'])
def add_password(user_id):
    data = request.get_json()
    site_name = data['site_name']
    password = data['password']

    user = User.query.get_or_404(user_id)
    password_hash = generate_password(password)

    new_password = Password(user_id=user.id, site_name=site_name, password_hash=password_hash)
    db.session.add(new_password)
    db.session.commit()

    return jsonify({"message": "Password added successfully"}), 201
