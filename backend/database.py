from pymongo import MongoClient
from config import Config
import os

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.connected = False
        self.connect()
    
    def connect(self):
        try:
            # Check if MONGO_URI is properly configured
            mongo_uri = Config.MONGO_URI
            if not mongo_uri or mongo_uri == "mongodb://localhost:27017/":
                print("Warning: Using default MongoDB URI. Please set MONGO_URI in .env file")
                # For development, we'll continue with local MongoDB
                mongo_uri = "mongodb://localhost:27017/"
            
            self.client = MongoClient(mongo_uri, 
                                    serverSelectionTimeoutMS=5000,
                                    connectTimeoutMS=5000,
                                    tlsAllowInvalidCertificates=True)
            
            # Test the connection
            self.client.server_info()
            self.db = self.client["eco_rewards"]
            self.users_collection = self.db["users"]
            self.connected = True
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Warning: Could not connect to MongoDB: {e}")
            print("Application will continue without database functionality")
            self.connected = False
            # Don't raise the exception - let the app continue
    
    def get_users_collection(self):
        if not self.connected:
            print("Warning: Database not connected. Please check your MongoDB configuration.")
            return None
        return self.users_collection
    
    def is_connected(self):
        return self.connected

# Global database instance
db_instance = Database()
