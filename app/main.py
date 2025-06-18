from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from app.api.routes import api_bp
from app.config import Config
import os

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize basic auth
auth = HTTPBasicAuth()

# Simple user storage - Add to .env for security
users = {
    os.getenv('DEMO_USERNAME', 'admin'): generate_password_hash(os.getenv('DEMO_PASSWORD', 'uva2025demo')),
    # Add more users if needed:
    # 'ashley': generate_password_hash('ashley123'),
    # 'susan': generate_password_hash('susan123'),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.before_request
def require_login():
    # Completely disable auth for now
    return None

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/setup')

def setup():
    env = request.args.get('env', '')
    return render_template('index.html', selected_env=env)

@app.route('/request')
def new_request():
    return render_template('request.html')

@app.route('/requests')
def requests_list():
    return render_template('requests_list.html')

@app.route('/request/<request_id>')

def request_details(request_id):
    return redirect(url_for('requests_list'))

@app.errorhandler(404)
def not_found(error):
    return {"error": "Resource not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500