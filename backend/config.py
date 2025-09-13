import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.urandom(24)
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ML Model paths (relative to backend directory)
    WASTE_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'classifyWaste.h5')
    YOLO_MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'YOLO', 'streamlit-detection-tracking - app', 'weights', 'best.pt')
