from flask import Blueprint, request, jsonify
import requests
from config import Config

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message or not Config.GEMINI_API_KEY:
        return jsonify({'reply': 'Sorry, the chatbot is not available.'})
    
    payload = {
        "contents": [{"parts": [{"text": user_message}]}]
    }
    
    try:
        r = requests.post(Config.GEMINI_API_URL, json=payload, timeout=10)
        r.raise_for_status()
        gemini_data = r.json()
        reply = gemini_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not reply:
            reply = "Sorry, I couldn't understand that."
        
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'Sorry, there was an error contacting Gemini.'})
