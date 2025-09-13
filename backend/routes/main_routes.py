from flask import Blueprint, request, render_template, redirect, session, url_for, jsonify
from auth.auth_service import AuthService
from services.achievement_service import AchievementService
from bson.objectid import ObjectId

main_bp = Blueprint('main', __name__)
auth_service = AuthService()
achievement_service = AchievementService()

@main_bp.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template("home.html")

@main_bp.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = auth_service.get_user_by_id(session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('auth.login'))
    
    user['classifications'] = len(user.get('classification_history', []))
    user['recent_activity'] = user.get('classification_history', [])[-5:]
    return render_template("dashboard.html", user=user)

@main_bp.route("/get_user_stats", methods=["GET"])
def get_user_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'No user session'}), 401
    
    user = auth_service.get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'eco_points': user['eco_points'],
        'classification_history': user['classification_history'],
        'achievements': user['achievements']
    })

@main_bp.route("/claim_reward", methods=["POST"])
def claim_reward():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    success, message = auth_service.claim_reward(session['user_id'])
    if success:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': message}), 400

@main_bp.route("/leaderboard", methods=["GET"])
def leaderboard():
    from database import db_instance
    users = db_instance.get_users_collection().find()
    leaderboard = []
    for user in users:
        leaderboard.append({
            'user_id': str(user['_id'])[-6:],
            'eco_points': user.get('eco_points', 0)
        })
    leaderboard = sorted(leaderboard, key=lambda x: x['eco_points'], reverse=True)[:10]
    return jsonify(leaderboard)

@main_bp.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
