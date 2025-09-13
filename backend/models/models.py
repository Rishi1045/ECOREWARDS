# models.py
# MongoDB User Schema (for documentation/reference)

user_schema = {
    'name': 'str',  # User's full name
    'email': 'str',  # User's email address (unique)
    'password': 'str',  # Hashed password
    'join_date': 'str',  # Date of registration (YYYY-MM-DD)
    'eco_points': 0,  # Integer, total eco points
    'classifications': 0,  # Integer, total classifications
    'rewards': 0,  # Integer, total rewards claimed
    'classification_history': [
        {
            'timestamp': 'str',  # Classification time (YYYY-MM-DD HH:MM:SS)
            'waste_type': 'str',  # Type of waste classified
            'points_earned': 0  # Points earned for this classification
        }
    ],
    'achievements': [
        'str'  # Achievement names (e.g., 'eco_beginner')
    ],
    'recent_classifications': 0  # Integer, classifications in last 7 days
}

# Note: This is for reference only. MongoDB is schemaless by default. 