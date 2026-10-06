import os
import certifi
from pymongo import MongoClient

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB""" 
        try:
            mongo_uri = os.environ.get('MONGODB_URI')
            if not mongo_uri:
                raise ValueError("MONGODB_URI is not set. Please check your config.env file.")
            
            # Use certifi to provide SSL certificate bundle for SRV or SSL connections
            if "srv" in mongo_uri or "ssl=true" in mongo_uri:
                self.client = MongoClient(mongo_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
            else:
                self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            
            self.db = self.client[os.environ.get('DB_NAME', 'plagiarism_detector')]
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas")
        except Exception as e:
            print(f"Warning: Primary MongoDB connection failed: {e}")
            try:
                local_uri = "mongodb://localhost:27017/"
                print(f"Attempting fallback connection to local MongoDB ({local_uri})...")
                self.client = MongoClient(local_uri, serverSelectionTimeoutMS=3000)
                self.db = self.client[os.environ.get('DB_NAME', 'plagiarism_detector')]
                self.client.admin.command('ping')
                print("✅ Successfully connected to local MongoDB!")
            except Exception as local_e:
                print(f"❌ Fallback connection to local MongoDB also failed: {local_e}")
                raise e
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        return self.db[collection_name]
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()

# Initialize database instance
db = Database()
