from flask import Flask, request, render_template, redirect, jsonify, session, flash, url_for
from flask_jsglue import JSGlue # this is use for url_for() working inside javascript which is help us to navigate the url
#from flask_cors import CORS
import util
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import hashlib
import secrets
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import requests
import base64
from io import BytesIO
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model

load_dotenv()

application = Flask(__name__)
application.secret_key = os.urandom(24)  # Required for session

# JSGlue is use for url_for() working inside javascript which is help us to navigate the url
jsglue = JSGlue() # create a object of JsGlue
jsglue.init_app(application) # and assign the app as a init app to the instance of JsGlue

# MongoDB setup
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.server_info()
    db = client["eco_rewards"]
    users_collection = db["users"]
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=" + GEMINI_API_KEY

# Load model and class labels once
realtime_model = load_model('classifyWaste.h5', compile=False)
realtime_class_labels = ["Batteries", "Clothes", "E-waste", "Glass", "Light Bulbs", "Metal", "Organic", "Paper", "Plastic"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

util.load_artifacts()
#home page
@application.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("home.html")

@application.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users_collection.find_one({"email": email})
        if user and user.get('password') == hash_password(password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template("auth.html", is_login=True)

@application.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template("auth.html", is_login=False)
        if users_collection.find_one({"email": email}):
            flash('Email already registered')
            return render_template("auth.html", is_login=False)
        user = {
            'name': name,
            'email': email,
            'password': hash_password(password),
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'eco_points': 0,
            'classifications': 0,
            'rewards': 0,
            'classification_history': [],
            'achievements': [],
            'recent_classifications': 0
        }
        result = users_collection.insert_one(user)
        session['user_id'] = str(result.inserted_id)
        return redirect(url_for('dashboard'))
    return render_template("auth.html", is_login=False)

@application.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('login'))
    user['classifications'] = len(user.get('classification_history', []))
    user['recent_activity'] = user.get('classification_history', [])[-5:]
    return render_template("dashboard.html", user=user)

@application.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

#classify waste
@application.route("/classifywaste", methods = ["POST"])
def classifywaste():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    image_data = request.files["file"]
    basepath = os.path.dirname(__file__)
    filename = secure_filename(image_data.filename)
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.jpg', '.jpeg', '.png']:
        image_path = os.path.join(basepath, "uploads", filename)
        image_data.save(image_path)
        predicted_value, details, video1, video2 = util.classify_waste(image_path)
        os.remove(image_path)
    else:
        image_bytes = image_data.read()
        predicted_value = util.classify_waste_bytes(image_bytes)
        details, video1, video2 = util.data[predicted_value][0], util.data[predicted_value][1], util.data[predicted_value][2]
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    if user:
        points_earned = 10
        new_activity = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'waste_type': predicted_value,
            'points_earned': points_earned
        }
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$push": {"classification_history": new_activity},
             "$inc": {"eco_points": points_earned}}
        )
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        check_achievements(user)
    return jsonify(
        predicted_value=predicted_value,
        details=details,
        video1=video1,
        video2=video2,
        eco_points=user['eco_points']
    )

@application.route("/claim_reward", methods=["POST"])
def claim_reward():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    if user['eco_points'] >= 100:
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$inc": {"eco_points": -100, "rewards": 1}}
        )
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Not enough points'}), 400

@application.route("/get_user_stats", methods=["GET"])
def get_user_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'No user session'}), 401
    user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'eco_points': user['eco_points'],
        'classification_history': user['classification_history'],
        'achievements': user['achievements']
    })

def get_points_for_waste_type(waste_type):
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

def check_achievements(user):
    achievements = user.get('achievements', [])
    updated = False
    if user['eco_points'] >= 1000 and 'eco_master' not in achievements:
        achievements.append('eco_master')
        updated = True
    elif user['eco_points'] >= 500 and 'eco_enthusiast' not in achievements:
        achievements.append('eco_enthusiast')
        updated = True
    elif user['eco_points'] >= 100 and 'eco_beginner' not in achievements:
        achievements.append('eco_beginner')
        updated = True
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
        users_collection.update_one({"_id": user['_id']}, {"$set": {"achievements": achievements}})
    return achievements

# here is route of 404 means page not found error
@application.errorhandler(404)
def page_not_found(e):
    # here i created my own 404 page which will be redirect when 404 error occured in this web app
    return render_template("404.html"), 404

@application.route("/leaderboard", methods=["GET"])
def leaderboard():
    users = users_collection.find()
    leaderboard = []
    for user in users:
        leaderboard.append({
            'user_id': str(user['_id'])[-6:],
            'eco_points': user.get('eco_points', 0)
        })
    leaderboard = sorted(leaderboard, key=lambda x: x['eco_points'], reverse=True)[:10]
    return jsonify(leaderboard)

@application.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message or not GEMINI_API_KEY:
        return jsonify({'reply': 'Sorry, the chatbot is not available.'})
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }
    try:
        r = requests.post(GEMINI_API_URL, json=payload, timeout=10)
        r.raise_for_status()
        gemini_data = r.json()
        reply = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        if not reply:
            reply = "Sorry, I couldn't understand that."
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'Sorry, there was an error contacting Gemini.'})

@application.route('/realtime')
def realtime():
    return render_template('realtime.html')

@application.route('/realtime_predict', methods=['POST'])
def realtime_predict():
    data = request.get_json()
    img_data = data.get('image', None)
    if not img_data:
        return jsonify({'label': 'No image', 'confidence': ''})
    # Remove header if present
    if ',' in img_data:
        img_data = img_data.split(',')[1]
    try:
        img_bytes = base64.b64decode(img_data)
        img = Image.open(BytesIO(img_bytes)).convert('RGB')
        img = img.resize((224, 224))
        arr = np.array(img).astype('float32') / 255.0
        arr = np.expand_dims(arr, axis=0)
        preds = realtime_model.predict(arr, verbose=0)
        pred_idx = int(np.argmax(preds[0]))
        confidence = float(preds[0][pred_idx])
        label = realtime_class_labels[pred_idx] if pred_idx < len(realtime_class_labels) else 'Unknown'
        return jsonify({'label': label, 'confidence': f'{confidence:.2f}'})
    except Exception as e:
        return jsonify({'label': 'Error', 'confidence': ''})

@application.route('/multi-waste')
def multi_waste():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('multi_waste.html')

@application.route('/multi-waste-classification', methods=['POST'])
def multi_waste_classification():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Process the image using YOLOv8
    result = util.process_multi_waste_image(file)
    
    if result['success']:
        # Update user's eco points and classification history
        points_earned = len(result['detections']) * 5  # 5 points per detection
        new_activity = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'waste_types': [det['class'] for det in result['detections']],
            'points_earned': points_earned
        }
        
        users_collection.update_one(
            {"_id": ObjectId(session['user_id'])},
            {"$push": {"classification_history": new_activity},
             "$inc": {"eco_points": points_earned}}
        )
        
        # Check for achievements
        user = users_collection.find_one({"_id": ObjectId(session['user_id'])})
        check_achievements(user)
    
    return jsonify(result)

if __name__ == "__main__":
    application.run()