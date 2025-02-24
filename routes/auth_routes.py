from app_instance import app
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.auth_utils import login_required
from app_instance import mongo

auth_bp = Blueprint('auth', __name__)
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

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users.find_one({'username': username})
    
    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/protected', methods=['GET'])
@login_required
def protected():
    return jsonify({'message': f'Hello, {session["username"]}!'}), 200
