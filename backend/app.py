import os
# Set environment variables before importing TensorFlow-related modules
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU usage
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'

from flask import Flask
from config import Config
from database import db_instance

def create_app():
    # Get absolute paths for templates and static folders
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(os.path.dirname(backend_dir), 'src', 'frontend', 'templates')
    static_dir = os.path.join(os.path.dirname(backend_dir), 'src', 'frontend', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config.from_object(Config)
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.main_routes import main_bp
    from routes.waste_routes import waste_bp
    from routes.chatbot_routes import chatbot_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(waste_bp)
    app.register_blueprint(chatbot_bp)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host='127.0.0.1', port=5001)
