#!/usr/bin/env python3
"""
Canvas-Compatible JWK Generator
Generates RSA keys in the exact format Canvas expects
"""

import json
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64
import uuid

def int_to_base64url(value):
    """Convert an integer to base64url encoding"""
    # Convert to bytes
    byte_length = (value.bit_length() + 7) // 8
    bytes_value = value.to_bytes(byte_length, 'big')
    
    # Base64url encode (no padding)
    return base64.urlsafe_b64encode(bytes_value).decode('ascii').rstrip('=')

def generate_canvas_compatible_jwk():
    """Generate RSA key pair in Canvas-compatible format"""
    
    print("🔑 Generating RSA key pair for Canvas LTI...")
    
    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()
    
    # Create JWK
    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": f"canvas-lti-{str(uuid.uuid4())[:8]}",
        "n": int_to_base64url(public_numbers.n),
        "e": int_to_base64url(public_numbers.e)
    }
    
    # Create JWKS (for your endpoint)
    jwks = {
        "keys": [jwk]
    }
    
    # Get private key in PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    return private_pem, jwks, jwk

def save_keys():
    """Generate and save all key files"""
    
    # Create keys
    private_pem, jwks, single_jwk = generate_canvas_compatible_jwk()
    
    # Create directory if it doesn't exist
    key_dir = os.path.join(os.path.dirname(__file__), 'keys')
    os.makedirs(key_dir, exist_ok=True)
    
    # Save private key
    private_key_path = os.path.join(key_dir, 'private.key')
    with open(private_key_path, 'w') as f:
        f.write(private_pem)
    
    # Save JWKS (for your /lti/jwks endpoint)
    jwks_path = os.path.join(key_dir, 'jwks.json')
    with open(jwks_path, 'w') as f:
        json.dump(jwks, f, indent=2)
    
    # Save single JWK (for Canvas registration)
    canvas_jwk_path = os.path.join(key_dir, 'canvas_public_key.json')
    with open(canvas_jwk_path, 'w') as f:
        json.dump(single_jwk, f, indent=2)
    
    print("✅ Keys generated successfully!")
    print(f"📁 Files saved in: {key_dir}")
    print()
    
    print("=" * 60)
    print("🎯 FOR CANVAS LTI 1.3 REGISTRATION")
    print("=" * 60)
    print("Copy this EXACT JSON into Canvas 'Public JWK' field:")
    print()
    print(json.dumps(single_jwk, indent=2))
    print()
    
    print("=" * 60)
    print("🌐 FOR YOUR JWKS ENDPOINT (/lti/jwks)")
    print("=" * 60)
    print("Your endpoint should return:")
    print()
    print(json.dumps(jwks, indent=2))
    print()
    
    print("=" * 60)
    print("📋 CANVAS SETUP CHECKLIST")
    print("=" * 60)
    print("1. ✅ Copy the single JWK above into Canvas")
    print("2. ✅ Set your JWKS URL to: https://canvas-test-automation-production.up.railway.app/lti/jwks")
    print("3. ✅ Update your private key path in config")
    print("4. ✅ Test the endpoints work before registering")
    print()
    
    return {
        'private_key_path': private_key_path,
        'jwks_path': jwks_path,
        'canvas_jwk_path': canvas_jwk_path,
        'single_jwk': single_jwk,
        'jwks': jwks
    }

def validate_jwk(jwk):
    """Basic validation of JWK format"""
    required_fields = ['kty', 'use', 'alg', 'kid', 'n', 'e']
    
    print("🔍 Validating JWK format...")
    for field in required_fields:
        if field not in jwk:
            print(f"❌ Missing required field: {field}")
            return False
        print(f"✅ {field}: {jwk[field][:20]}..." if len(str(jwk[field])) > 20 else f"✅ {field}: {jwk[field]}")
    
    print("✅ JWK format looks good!")
    return True

if __name__ == "__main__":
    print("🚀 Canvas LTI 1.3 Key Generator")
    print("=" * 60)
    
    try:
        result = save_keys()
        
        # Validate the generated key
        validate_jwk(result['single_jwk'])
        
        print("\n🎉 All done! Use the JWK above in Canvas.")
        
    except Exception as e:
        print(f"❌ Error generating keys: {e}")
        print("💡 Make sure you have 'cryptography' installed:")
        print("   pip install cryptography")