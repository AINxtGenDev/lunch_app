# config.py
import os

# Get the absolute path of the directory where the script is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Flask App Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'you-should-change-this')
DEBUG = True

# Database Configuration
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Application-specific Configuration
FLIPSNACK_CONFIG = {
    'base_url': 'https://www.flipsnack.com/',
    'publication_pattern': r'wochenmen.*\.html',
    'retry_attempts': 3,
    'pdf_parse_method': 'pypdf2'  # Options: 'pypdf2', 'pdfplumber', 'ocr'
}

