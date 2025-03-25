import jwt
import datetime
import os
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.auth_utils import token_required
from app_instance import mongo

auth_bp = Blueprint('auth', __name__)

# Secret key for signing JWTs (set this in environment variables)
SECRET_KEY = os.getenv("SECRET_KEY")

def generate_token(user_id):
    """Generate JWT token for authentication."""
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Token expires in 2 hours
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

@auth_bp.route('/register', methods=['POST'])
def register():
    users = mongo.db.users
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if users.find_one({'username': username}):
        return jsonify({'error': 'Username already exists'}), 400

    hashed_password = generate_password_hash(password)
    users.insert_one({'username': username, 'password': hashed_password})

    return jsonify({'message': 'User registered successfully'}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users.find_one({'username': username})
    
    if user and check_password_hash(user['password'], password):
        token = generate_token(user["_id"])
        return jsonify({'message': 'Login successful', 'token': token}), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Since we're using JWT, the logout will be handled client-side (e.g., removing token from storage)
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/protected', methods=['GET'])
@token_required  # This decorator will check the JWT token in the headers
def protected(current_user):
    return jsonify({'message': f'Hello, {current_user["username"]}!'}), 200
