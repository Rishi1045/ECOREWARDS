from flask import Blueprint, request, render_template, redirect, session, url_for, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from services.ml_service import MLService
from auth.auth_service import AuthService
from services.achievement_service import AchievementService

waste_bp = Blueprint('waste', __name__)

# Lazy initialization of services
ml_service = None
auth_service = None
achievement_service = None

def get_ml_service():
    global ml_service
    if ml_service is None:
        ml_service = MLService()
    return ml_service

def get_auth_service():
    global auth_service
    if auth_service is None:
        auth_service = AuthService()
    return auth_service

def get_achievement_service():
    global achievement_service
    if achievement_service is None:
        achievement_service = AchievementService()
    return achievement_service

@waste_bp.route("/classifywaste", methods=["POST"])
def classifywaste():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    image_data = request.files["file"]
    basepath = os.path.dirname(__file__)
    filename = secure_filename(image_data.filename)
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.jpg', '.jpeg', '.png']:
        upload_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        image_path = os.path.join(upload_dir, filename)
        image_data.save(image_path)
        predicted_value, details, video1, video2 = get_ml_service().classify_waste(image_path)
        os.remove(image_path)
    else:
        image_bytes = image_data.read()
        predicted_value = get_ml_service().classify_waste_bytes(image_bytes)
        details, video1, video2 = get_ml_service().data[predicted_value][0], get_ml_service().data[predicted_value][1], get_ml_service().data[predicted_value][2]
    
    user = get_auth_service().get_user_by_id(session['user_id'])
    if user:
        points_earned = 10
        new_activity = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'waste_type': predicted_value,
            'points_earned': points_earned
        }
        get_auth_service().update_user_points(session['user_id'], points_earned, new_activity)
        user = get_auth_service().get_user_by_id(session['user_id'])
        get_achievement_service().check_achievements(user)
    
    return jsonify(
        predicted_value=predicted_value,
        details=details,
        video1=video1,
        video2=video2,
        eco_points=user['eco_points']
    )

@waste_bp.route('/realtime')
def realtime():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('realtime.html')

@waste_bp.route('/realtime_predict', methods=['POST'])
def realtime_predict():
    data = request.get_json()
    img_data = data.get('image', None)
    if not img_data:
        return jsonify({'label': 'No image', 'confidence': ''})
    
    result = get_ml_service().realtime_predict(img_data)
    return jsonify(result)

@waste_bp.route('/multi-waste')
def multi_waste():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('multi_waste.html')

@waste_bp.route('/multi-waste-classification', methods=['POST'])
def multi_waste_classification():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    result = get_ml_service().process_multi_waste_image(file)
    
    if result['success']:
        points_earned = len(result['detections']) * 5
        new_activity = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'waste_types': [det['class'] for det in result['detections']],
            'points_earned': points_earned
        }
        
        get_auth_service().update_user_points(session['user_id'], points_earned, new_activity)
        user = get_auth_service().get_user_by_id(session['user_id'])
        get_achievement_service().check_achievements(user)
    
    return jsonify(result)