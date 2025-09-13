# Vercel entry point
import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
sys.path.insert(0, os.path.dirname(backend_dir))

from app import create_app

app = create_app()

# This is the WSGI application that Vercel will use
application = app

if __name__ == "__main__":
    app.run()
