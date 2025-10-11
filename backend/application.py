from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# Import routes
from routes.auth import auth_bp
from routes.plagiarism import plagiarism_bp

def create_app():
    application = Flask(__name__)
    
    # Configuration
    jwt_secret = os.environ.get('JWT_SECRET_KEY')
    if not jwt_secret:
        raise ValueError("JWT_SECRET_KEY is not set in the environment. Please configure it in your hosting service.")
    application.config['JWT_SECRET_KEY'] = jwt_secret
    application.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire
    
    # Initialize extensions
    CORS(application, origins=["https://plaghunt.netlify.app"])  # Allow React frontend
    jwt = JWTManager(application)
    
    # Register blueprints
    application.register_blueprint(auth_bp, url_prefix='/api/auth')
    application.register_blueprint(plagiarism_bp, url_prefix='/api/plagiarism')
    
    # Health check endpoint
    @application.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy", 
            "message": "Plagiarism Detection API is running",
            "version": "2.0.0"
        })
    
    # Error handlers
    @application.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @application.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "Invalid token"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"error": "Authorization token is required"}), 401
    
    return application

# The Flask app must be created at the module level for Gunicorn to find it
application = create_app()

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5001)
