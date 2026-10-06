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
        
        if not user or 'password' not in user:
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            user['_id'] = str(user['_id'])
            user.pop('password', None)  # Don't return password
            return user
        
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
                user.pop('password', None)  # Don't return password
                return user
            return None
        except Exception as e:
            print(f"Error in get_user_by_id: {e}")
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

    def find_or_create_google_user(self, email, google_id, username, picture=None):
        """Find user by email or create a new user via Google OAuth"""
        user = self.collection.find_one({"email": email})
        
        if user:
            update_fields = {}
            if not user.get('google_id'):
                update_fields['google_id'] = google_id
            if picture and not user.get('picture'):
                update_fields['picture'] = picture
            if update_fields:
                update_fields['updated_at'] = datetime.utcnow()
                self.collection.update_one({"_id": user['_id']}, {"$set": update_fields})
            
            user['_id'] = str(user['_id'])
            if 'password' in user:
                del user['password']
            return user
        
        # Generate clean unique username
        base_username = (username or email.split('@')[0]).replace(' ', '_').lower()
        final_username = base_username
        counter = 1
        while self.collection.find_one({"username": final_username}):
            final_username = f"{base_username}{counter}"
            counter += 1
        
        user_data = {
            "username": final_username,
            "email": email,
            "google_id": google_id,
            "picture": picture,
            "auth_provider": "google",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = self.collection.insert_one(user_data)
        user_data['_id'] = str(result.inserted_id)
        return user_data
