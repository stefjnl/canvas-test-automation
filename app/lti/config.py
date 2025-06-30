import os
import json
import tempfile
from pylti1p3.tool_config import ToolConfJsonFile

class LTIConfig:
    @staticmethod
    def get_lti_config_path():
        return os.path.join(os.path.dirname(__file__), 'config.json')
    
    @staticmethod
    def get_private_key_path():
        """Create private key file from environment variable"""
        private_key_content = os.getenv('LTI_PRIVATE_KEY')
        if not private_key_content:
            raise Exception("LTI_PRIVATE_KEY environment variable not set")
        
        # Create the private key file in the lti directory
        private_key_path = os.path.join(os.path.dirname(__file__), 'private.key')
        
        # Write the private key content to file
        with open(private_key_path, 'w') as f:
            f.write(private_key_content)
        
        return private_key_path
    
    @staticmethod
    def create_tool_conf():
        return ToolConfJsonFile(LTIConfig.get_lti_config_path())
    
    @staticmethod
    def setup_lti_config(client_id, deployment_id, platform_url, auth_url, token_url, jwks_url):
        """Create the LTI configuration file"""
        
        # Create private key file from environment variable
        private_key_path = LTIConfig.get_private_key_path()
        
        config = {
            platform_url: [{
                "default": True,
                "client_id": client_id,
                "auth_login_url": auth_url,
                "auth_token_url": token_url,
                "auth_audience": None,
                "key_set_url": jwks_url,
                "key_set": None,
                "private_key_file": private_key_path,  # Use file path, not content
                "public_key_file": None,
                "deployment_ids": [deployment_id]
            }]
        }
        
        config_path = LTIConfig.get_lti_config_path()
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ LTI config created with private key at: {private_key_path}")
        return config