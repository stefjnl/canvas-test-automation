from flask import Flask, render_template, request, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from app.api.routes import api_bp
from app.config import Config
import os

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Session configuration for LTI
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'sessions')
app.config['SESSION_COOKIE_NAME'] = 'canvas_test_automation_session'
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for LTI iframe

Session(app)
CORS(app, supports_credentials=True)

# Register blueprints (only once!)
app.register_blueprint(api_bp, url_prefix='/api')

# Try to register LTI blueprint, but don't fail if it has issues
try:
    from app.lti.routes import lti_bp
    app.register_blueprint(lti_bp, url_prefix='/lti')
    print("LTI blueprint registered successfully")
except Exception as e:
    print(f"Warning: Could not register LTI blueprint: {e}")

def check_lti_session():
    """Check if user has valid LTI session"""
    return session.get('lti_launch', False)

@app.before_request
def require_login():
    # Completely disable auth for now
    return None

# Routes
@app.route('/health')
def health_check():
    return {"status": "healthy", "timestamp": "2025-06-24"}, 200

@app.route('/')
def dashboard():
    # Check if this is an LTI launch
    if request.args.get('lti'):
        if not check_lti_session():
            return "Unauthorized - Please launch from Canvas", 401
    return render_template('dashboard.html',
                         lti_mode=check_lti_session(),
                         user_name=session.get('canvas_user_name', 'Guest'))

@app.route('/setup')
def setup():
    if check_lti_session() and not session.get('is_instructor'):
        return "Instructor access required", 403
    env = request.args.get('env', '')
    return render_template('index.html',
                         selected_env=env,
                         lti_mode=check_lti_session())

@app.route('/request')
def new_request():
    if check_lti_session() and not session.get('is_instructor'):
        return "Instructor access required", 403
    return render_template('request.html',
                         lti_mode=check_lti_session())

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