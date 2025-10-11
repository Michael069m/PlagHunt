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
            
            # Use certifi to provide the SSL certificate bundle
            self.client = MongoClient(mongo_uri, tlsCAFile=certifi.where())
            
            self.db = self.client[os.environ.get('DB_NAME', 'plagiarism_detector')]
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
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
