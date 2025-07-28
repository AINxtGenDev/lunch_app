# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Get the absolute base directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration with security best practices."""
    
    # Security Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    
    # Session Security
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Database Configuration - Use absolute path
    # Option 1: Simple relative path (SQLAlchemy will handle it)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "instance", "app.db")}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT_LIMITS = ["200 per day", "50 per hour"]
    
    # CORS Configuration
    CORS_ORIGINS = []
    
    # Scraping Configuration
    SCRAPING_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    SCRAPING_TIMEOUT = 30
    SCRAPING_RETRY_COUNT = 3
    SCRAPING_RETRY_DELAY = 5


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
