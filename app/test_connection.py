import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Get credentials
base_url = os.getenv('CANVAS_API_URL')
token = os.getenv('CANVAS_API_TOKEN')

# Test API call - get your user info
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(f"{base_url}/users/self", headers=headers)

if response.status_code == 200:
    user = response.json()
    print(f"✅ Connection successful!")
    print(f"Logged in as: {user.get('name', 'Unknown')}")
    print(f"User ID: {user.get('id')}")
else:
    print(f"❌ Connection failed: {response.status_code}")
    print(response.text)

response = requests.get(f"{base_url}/accounts", headers=headers)
if response.status_code == 200:
    accounts = response.json()
    print("\nAvailable accounts:")
    for account in accounts:
        print(f"- ID: {account['id']}, Name: {account['name']}")