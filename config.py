import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    # Google API Configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
    
    # AI Model Configuration
    MODEL_NAME = os.environ.get('MODEL_NAME') or 'gpt-4'
    API_KEY = os.environ.get('AI_API_KEY')
    
    # Application Configuration
    DEBUG = os.environ.get('DEBUG') == 'True'
    TESTING = os.environ.get('TESTING') == 'True'
    
    # Database Configuration (if needed in the future)
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///app.db'