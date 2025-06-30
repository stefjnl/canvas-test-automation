# Add this to your main.py or create a separate setup script
# Run this ONCE to initialize LTI configuration

import os
from app.lti.config import LTIConfig

def setup_lti():
    """Initialize LTI configuration for Canvas"""
    
    # Get deployment ID - you'll need to find this in Canvas
    deployment_id = os.getenv('LTI_DEPLOYMENT_ID', '1')  # Often just '1' for single deployment
    
    config = LTIConfig.setup_lti_config(
        client_id='104400000000000323',
        deployment_id=deployment_id,
        platform_url='https://uvadlo-dev.instructure.com',
        auth_url='https://uvadlo-dev.instructure.com/api/lti/authorize_redirect',
        token_url='https://uvadlo-dev.instructure.com/login/oauth2/token',
        jwks_url='https://uvadlo-dev.instructure.com/api/lti/security/jwks'
    )
    
    print("LTI configuration created successfully!")
    return config

# Run this once
if __name__ == "__main__":
    setup_lti()