import os
import json
from pylti1p3.tool_config import ToolConfJsonFile
from pylti1p3.registration import Registration

class LTIConfig:
    @staticmethod
    def get_lti_config_path():
        return os.path.join(os.path.dirname(__file__), 'config.json')
    
    @staticmethod
    def get_jwks_path():
        # Use relative path instead of absolute
        return os.path.join(os.path.dirname(__file__), 'private.key')
    
    @staticmethod
    def create_tool_conf():
        return ToolConfJsonFile(LTIConfig.get_lti_config_path())
    
    @staticmethod
    def setup_lti_config(client_id, deployment_id, platform_url, auth_url, token_url, jwks_url):
        """Create the LTI configuration file"""
        
        # Use relative path for private key
        private_key_path = LTIConfig.get_jwks_path()
        
        config = {
            platform_url: [{
                "default": True,
                "client_id": client_id,
                "auth_login_url": auth_url,
                "auth_token_url": token_url,
                "auth_audience": None,
                "key_set_url": jwks_url,
                "key_set": None,
                "private_key_file": private_key_path,  # Fixed: use relative path
                "public_key_file": None,
                "deployment_ids": [deployment_id]
            }]
        }
        
        config_path = LTIConfig.get_lti_config_path()
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"LTI config saved to: {config_path}")
        print(f"Private key path: {private_key_path}")
        
        return config