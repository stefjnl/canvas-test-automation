import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    CANVAS_API_URL = os.getenv('CANVAS_API_URL')
    CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')
    
    # Test environments
    TEST_ENVIRONMENTS = {
        'acceptatie': os.getenv('TEST_ENV_ACCEPTATIE'),
        'tes': os.getenv('TEST_ENV_TES'),
        'development': os.getenv('TEST_ENV_DEVELOPMENT')
    }