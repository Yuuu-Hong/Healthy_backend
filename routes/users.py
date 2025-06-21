from flask import Blueprint, request, jsonify
from models import User, db

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })
    return jsonify(result)

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email}), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    db.session.commit()
    return jsonify({"id": user.id, "username": user.username, "email": user.email})

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'})