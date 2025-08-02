import os
from datetime import timedelta

class ProductionConfig:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///Data/inventory.db')
    
    # Paradigm ERP Configuration
    PARADIGM_API_KEY = os.environ.get('PARADIGM_API_KEY', 'nVPsQFBteV&GEd7*8n0%RliVjksag8')
    PARADIGM_USERNAME = os.environ.get('PARADIGM_USERNAME', 'web_admin')
    PARADIGM_PASSWORD = os.environ.get('PARADIGM_PASSWORD', 'ChangeMe#123!')
    PARADIGM_BASE_URL = os.environ.get('PARADIGM_BASE_URL', 'https://greenfieldapi.para-apps.com')
    
    # Performance Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'production.log')