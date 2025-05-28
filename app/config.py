import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    CANVAS_API_URL = os.getenv('CANVAS_API_URL')
    CANVAS_API_TOKEN = os.getenv('CANVAS_API_TOKEN')
    
    # Test environments
    TEST_ENVIRONMENTS = {
        'acceptatie': os.getenv('TEST_ENV_ACCEPTATIE'),
        'test': os.getenv('TEST_ENV_TEST'),
        'development': os.getenv('TEST_ENV_DEVELOPMENT')
    }