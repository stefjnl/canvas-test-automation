import os

class Config:
    """Flask application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Canvas API Configuration
    CANVAS_API_URL = os.getenv('CANVAS_API_URL', '')
    CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN', '')
    
    # Test Environment URLs
    TEST_ENV_DEVELOPMENT = os.getenv('TEST_ENV_DEVELOPMENT', '')
    TEST_ENV_TEST = os.getenv('TEST_ENV_TEST', '')
    TEST_ENV_ACCEPTATIE = os.getenv('TEST_ENV_ACCEPTATIE', '')