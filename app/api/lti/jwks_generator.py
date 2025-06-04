import json
from jwcrypto import jwk

def generate_jwks():
    """Generate a JSON Web Key Set for LTI"""
    # Generate RSA key
    key = jwk.JWK.generate(kty='RSA', size=2048)
    
    # Get private key in PEM format
    private_key = key.export_to_pem(private_key=True, password=None)
    
    # Get public key in JWK format
    public_key = json.loads(key.export_public())
    public_key['alg'] = 'RS256'
    public_key['use'] = 'sig'
    
    # Create JWKS
    jwks = {
        "keys": [public_key]
    }
    
    return private_key.decode('utf-8'), jwks

# Run this once to generate keys
if __name__ == "__main__":
    import os
    
    private_key, jwks = generate_jwks()
    
    # Save private key
    key_path = os.path.join(os.path.dirname(__file__), 'private.key')
    with open(key_path, 'w') as f:
        f.write(private_key)
    
    # Save JWKS
    jwks_path = os.path.join(os.path.dirname(__file__), 'jwks.json')
    with open(jwks_path, 'w') as f:
        json.dump(jwks, f, indent=2)
    
    print("Keys generated successfully!")
    print(f"\nAdd this JWKS URL to Canvas: https://your-domain.com/lti/jwks")
    print(f"\nJWKS content to serve:")
    print(json.dumps(jwks, indent=2))