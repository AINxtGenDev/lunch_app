# run.py
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, socketio, db

# Get configuration
config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name=config_name)

if __name__ == "__main__":
    # Security: In production, use a proper WSGI server like Gunicorn
    socketio.run(
        app,
        host="127.0.0.1",  # Bind to localhost only in development
        port=7000,
        debug=app.debug,
        use_reloader=app.debug,
    )
