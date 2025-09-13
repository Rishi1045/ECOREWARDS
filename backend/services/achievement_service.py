from bson.objectid import ObjectId
from database import db_instance

class AchievementService:
    def __init__(self):
        self.users_collection = db_instance.get_users_collection()
    
    def check_achievements(self, user):
        """Check and update user achievements"""
        achievements = user.get('achievements', [])
        updated = False
        
        # Eco points achievements
        if user['eco_points'] >= 1000 and 'eco_master' not in achievements:
            achievements.append('eco_master')
            updated = True
        elif user['eco_points'] >= 500 and 'eco_enthusiast' not in achievements:
            achievements.append('eco_enthusiast')
            updated = True
        elif user['eco_points'] >= 100 and 'eco_beginner' not in achievements:
            achievements.append('eco_beginner')
            updated = True
        
        # Classification count achievements
        classification_count = len(user.get('classification_history', []))
        if classification_count >= 100 and 'waste_warrior' not in achievements:
            achievements.append('waste_warrior')
            updated = True
        elif classification_count >= 50 and 'waste_hero' not in achievements:
            achievements.append('waste_hero')
            updated = True
        elif classification_count >= 10 and 'waste_starter' not in achievements:
            achievements.append('waste_starter')
            updated = True
        
        if updated:
            self.users_collection.update_one(
                {"_id": user['_id']}, 
                {"$set": {"achievements": achievements}}
            )
        
        return achievements
    
    def get_points_for_waste_type(self, waste_type):
        """Get points for specific waste type"""
        points_map = {
            'paper': 10,
            'plastic': 15,
            'glass': 20,
            'metal': 25,
            'organic': 5,
            'electronic': 30,
            'textile': 8,
            'hazardous': 35,
            'other': 3
        }
        return points_map.get(waste_type.lower(), 5)
