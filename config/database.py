import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        self.db_name = os.getenv('DATABASE_NAME', 'contract_simplifier')
        self.client = None
        self.db = None
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri)
            self.db = self.client[self.db_name]
            # Test the connection
            self.client.server_info()
            print(f"✓ Successfully connected to MongoDB database: {self.db_name}")
            return self.db
        except Exception as e:
            print(f"✗ Error connecting to MongoDB: {e}")
            return None
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        if self.db is not None:
            return self.db[collection_name]
        else:
            print("Database not connected. Call connect() first.")
            return None
    
    def close(self):
        """Close the database connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")

# Create a global database instance
db_instance = Database()