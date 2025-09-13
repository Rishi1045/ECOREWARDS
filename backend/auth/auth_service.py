import hashlib
from datetime import datetime
from bson.objectid import ObjectId
from database import db_instance

class AuthService:
    def __init__(self):
        self.users_collection = db_instance.get_users_collection()
    
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, name, email, password):
        """Create a new user account"""
        if self.users_collection.find_one({"email": email}):
            return None, "Email already registered"
        
        user = {
            'name': name,
            'email': email,
            'password': self.hash_password(password),
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'eco_points': 0,
            'classifications': 0,
            'rewards': 0,
            'classification_history': [],
            'achievements': [],
            'recent_classifications': 0
        }
        
        result = self.users_collection.insert_one(user)
        return str(result.inserted_id), None
    
    def authenticate_user(self, email, password):
        """Authenticate user login"""
        user = self.users_collection.find_one({"email": email})
        if user and user.get('password') == self.hash_password(password):
            return str(user['_id']), None
        return None, "Invalid email or password"
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            return user
        except:
            return None
    
    def update_user_points(self, user_id, points_earned, activity):
        """Update user's eco points and add activity to history"""
        try:
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"classification_history": activity},
                 "$inc": {"eco_points": points_earned}}
            )
            return True
        except:
            return False
    
    def claim_reward(self, user_id):
        """Claim reward for user"""
        try:
            user = self.get_user_by_id(user_id)
            if not user or user['eco_points'] < 100:
                return False, "Not enough points"
            
            self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$inc": {"eco_points": -100, "rewards": 1}}
            )
            return True, "Reward claimed successfully"
        except:
            return False, "Error claiming reward"
