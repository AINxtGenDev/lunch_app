# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import logging
from logging.handlers import RotatingFileHandler
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_name='development'):
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Import config
    from config import config
    app.config.from_object(config[config_name])
    
    # Get the project root directory (parent of app directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure instance directory exists
    instance_path = os.path.join(project_root, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path, exist_ok=True)
        app.logger.info(f"Created instance directory at: {instance_path}")
    
    # Initialize Flask extensions
    db.init_app(app)
    socketio.init_app(app, 
                     async_mode="eventlet",
                     cors_allowed_origins=app.config.get('CORS_ORIGINS', []))
    limiter.init_app(app)
    
    # Configure logging
    if not app.debug and not app.testing:
        logs_path = os.path.join(project_root, 'logs')
        if not os.path.exists(logs_path):
            os.makedirs(logs_path, exist_ok=True)
            
        file_handler = RotatingFileHandler(
            os.path.join(logs_path, 'lunch_menu_app.log'),
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Lunch Menu App startup')

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        # Import models here to avoid circular imports
        from . import models
        
        # Create database tables
        db.create_all()
        app.logger.info("Database tables created/verified")

        # Initialize scraping service
        try:
            from .services.scraping_service import ScrapingService
            scraping_service = ScrapingService()
            
            # Skip initial scrape if in debug mode to speed up development
            if not app.debug:
                app.logger.info("Performing initial scrape on application startup...")
                try:
                    scraping_service.run_all_scrapers()
                except Exception as e:
                    app.logger.error(f"Initial scrape failed: {e}", exc_info=True)
            else:
                app.logger.info("Debug mode: Skipping initial scrape")
            
            # Schedule daily updates
            scheduler = BackgroundScheduler(daemon=True)
            scheduler.add_job(
                scraping_service.run_all_scrapers, 
                "cron", 
                hour=5, 
                minute=0,
                misfire_grace_time=3600
            )
            scheduler.start()
            app.logger.info("Scheduler started. Daily scrape scheduled for 05:00.")
            
        except ImportError as e:
            app.logger.error(f"Failed to import scraping service: {e}")
        except Exception as e:
            app.logger.error(f"Failed to initialize scraping service: {e}", exc_info=True)

    return app
