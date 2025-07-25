# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_class=Config):
    """
    Creates and configures the Flask application.
    This is the application factory pattern.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Flask extensions here
    db.init_app(app)
    # We use eventlet as the async_mode for performance and compatibility
    socketio.init_app(app, async_mode='eventlet')

    # Register blueprints here
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Create database tables if they don't exist
    with app.app_context():
        from . import models # Import models here to avoid circular imports
        db.create_all()

    return app
