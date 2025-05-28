# create test_canvasapi.py
from app.api.canvas_client import CanvasClient

client = CanvasClient()
print(f"Connected as: {client.current_user.name}")

# Get root account
root = client.get_root_account()
print(f"Root account: {root['name']} (ID: {root['id']})")

# Get environment status
status = client.get_environment_status()
print(f"Environment status: {status}")