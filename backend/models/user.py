from models.database import db
from datetime import datetime
from bson.objectid import ObjectId
import bcrypt

class User:
    def __init__(self):
        self.collection = db.get_collection('users')
    
    def create_user(self, username, email, password):
        """Create a new user"""
        # Check if user already exists
        existing_user = self.collection.find_one({
            "$or": [{"username": username}, {"email": email}]
        })
        
        if existing_user:
            return {"error": "User already exists"}, 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_data = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(user_data)
        return {"user_id": str(result.inserted_id)}, 201
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        user = self.collection.find_one({"username": username})
        
        if not user:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            user['_id'] = str(user['_id'])
            del user['password']  # Don't return password
            return user
        
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                del user['password']  # Don't return password
                return user
            return None
        except:
            return None
    
    def update_user(self, user_id, update_data):
        """Update user information"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except:
            return False
