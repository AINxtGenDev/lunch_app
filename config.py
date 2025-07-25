# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    # SECURITY WARNING: Don't use this secret key in production!
    # Generate a real one with `python -c 'import secrets; print(secrets.token_hex())'`
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-that-you-should-change'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # App specific config
    RESTAURANTS_TO_SCRAPE = {
        'Erste Campus': 'https://erstecampus.at/en/kantine-am-campus-menu/',
        '4o4': 'https://4oh4.at/en/lunch-menu-en/',
        'Henry': 'https://www.enjoyhenry.com/menuplan-bdo/',
        'Kekko Sushi': 'https://www.kekkosushi.com/menu/',
        'IKI': 'https://iki-restaurant.at/wp-content/uploads/sites/2/2025/07/Lunch-KW-30.pdf' # Note: This URL is likely to change weekly
    }
