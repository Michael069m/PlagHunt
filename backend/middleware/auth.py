from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

def auth_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({"error": "Invalid token"}), 401
            
            # Verify user exists
            user_model = User()
            user = user_model.get_user_by_id(current_user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
            
            # Add user to request context
            request.current_user = user
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Authentication failed"}), 401
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Try to get user if token is provided
            if 'Authorization' in request.headers:
                current_user_id = get_jwt_identity()
                if current_user_id:
                    user_model = User()
                    user = user_model.get_user_by_id(current_user_id)
                    request.current_user = user
                else:
                    request.current_user = None
            else:
                request.current_user = None
        except:
            request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function
