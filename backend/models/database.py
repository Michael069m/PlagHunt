from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            self.client = MongoClient(mongo_uri)
            self.db = self.client[os.getenv('DB_NAME', 'plagiarism_detector')]
            # Test connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB")
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
