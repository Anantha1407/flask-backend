import jwt
import os
from functools import wraps
from flask import request, jsonify
from app_instance import mongo
from bson.objectid import ObjectId

SECRET_KEY = os.getenv("SECRET_KEY")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            token = token.split(" ")[1]  # Remove "Bearer " prefix if present
            decoded_data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"_id":ObjectId(decoded_data["user_id"])})
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401

            return f(current_user, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

    return decorated
