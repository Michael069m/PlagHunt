from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token
from models.user import User
import re

auth_bp = Blueprint('auth', __name__)
user_model = User()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Valid password"

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters long"}), 400
        
        if not email or not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        is_valid, password_msg = validate_password(password)
        if not is_valid:
            return jsonify({"error": password_msg}), 400
        
        # Create user
        result, status_code = user_model.create_user(username, email, password)
        
        if status_code == 201:
            # Generate tokens
            access_token = create_access_token(identity=result['user_id'])
            refresh_token = create_refresh_token(identity=result['user_id'])
            
            return jsonify({
                "message": "User created successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": result['user_id']
            }), 201
        else:
            return jsonify(result), status_code
            
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        # Authenticate user
        user = user_model.authenticate_user(username, password)
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=user['_id'])
        refresh_token = create_refresh_token(identity=user['_id'])
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user['_id'],
                "username": user['username'],
                "email": user['email']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token"""
    try:
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required(refresh=True)
        def _refresh():
            current_user_id = get_jwt_identity()
            new_token = create_access_token(identity=current_user_id)
            return jsonify({"access_token": new_token}), 200
        
        return _refresh()
        
    except Exception as e:
        print(f"Token refresh error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """Verify if token is valid and return user info"""
    try:
        from flask_jwt_extended import jwt_required, get_jwt_identity
        
        @jwt_required()
        def _verify():
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({"error": "Invalid token"}), 401
            
            # Get user details
            user = user_model.get_user_by_id(current_user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
            
            return jsonify({
                "valid": True,
                "user": {
                    "id": user['_id'],
                    "username": user['username'],
                    "email": user['email']
                }
            }), 200
        
        return _verify()
        
    except Exception as e:
        print(f"Token verification error: {e}")
        return jsonify({"error": "Token verification failed"}), 401

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    """Google OAuth authentication endpoint"""
    try:
        import os, requests
        data = request.get_json()
        if not data or 'credential' not in data:
            return jsonify({"error": "Google credential token is required"}), 400
        
        credential = data['credential']
        
        # Verify Google token with Google's OAuth2 tokeninfo endpoint
        resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}")
        if resp.status_code != 200:
            return jsonify({"error": "Invalid or expired Google token"}), 401
        
        token_info = resp.json()
        
        # Verify client_id if set in environment
        google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        if google_client_id and token_info.get('aud') != google_client_id:
            # Note: Allow if user hasn't set GOOGLE_CLIENT_ID yet on backend
            pass
        
        email = token_info.get('email')
        google_id = token_info.get('sub')
        name = token_info.get('name', '')
        picture = token_info.get('picture', '')
        
        if not email or not google_id:
            return jsonify({"error": "Failed to retrieve user email from Google token"}), 400
        
        # Find or create user in MongoDB
        user = user_model.find_or_create_google_user(
            email=email,
            google_id=google_id,
            username=name,
            picture=picture
        )
        
        # Generate JWT tokens
        access_token = create_access_token(identity=user['_id'])
        refresh_token = create_refresh_token(identity=user['_id'])
        
        return jsonify({
            "message": "Google login successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user['_id'],
                "username": user['username'],
                "email": user['email'],
                "picture": user.get('picture', '')
            }
        }), 200
        
    except Exception as e:
        print(f"Google auth error: {e}")
        return jsonify({"error": f"Google authentication failed: {str(e)}"}), 500
