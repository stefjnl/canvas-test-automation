import os
import json
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.registration import Registration

class LTIConfig:
    @staticmethod
    def get_lti_config_path():
        return os.path.join(os.path.dirname(__file__), 'config.json')
    
    @staticmethod
    def get_private_key():
        """Get private key from environment variable"""
        return os.getenv('LTI_PRIVATE_KEY')
    
    @staticmethod
    def create_tool_conf():
        return ToolConfJsonFile(LTIConfig.get_lti_config_path())
    
    @staticmethod
    def setup_lti_config(client_id, deployment_id, platform_url, auth_url, token_url, jwks_url):
        """Create the LTI configuration file"""
        config = {
            platform_url: [{
                "default": True,
                "client_id": client_id,
                "auth_login_url": auth_url,
                "auth_token_url": token_url,
                "auth_audience": None,
                "key_set_url": jwks_url,
                "key_set": None,
                "private_key": LTIConfig.get_private_key(),  # Use environment variable
                "public_key_file": None,
                "deployment_ids": [deployment_id]
            }]
        }
        
        config_path = LTIConfig.get_lti_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config