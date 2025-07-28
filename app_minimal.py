# app_minimal.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_minimal_app():
    """Minimal app for testing without all the extensions."""
    app = Flask(__name__)
    
    # Use simple configuration
    app.config['SECRET_KEY'] = 'test-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure instance folder exists
    instance_path = os.path.join(app.root_path, 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        # Import models to register them
        from app import models
        db.create_all()
    
    return app
