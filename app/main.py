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

# Setup LTI config using the new Flask pattern
def setup_lti_config():
    """Ensure LTI config exists on Railway"""
    try:
        from app.lti.config import LTIConfig
        import os
        
        # Only create if it doesn't exist
        config_path = LTIConfig.get_lti_config_path()
        if not os.path.exists(config_path):
            LTIConfig.setup_lti_config(
                client_id='104400000000000323',
                deployment_id='EFkkYVAH4rEUxG9nUntayfyXD6BA6a6xfAHz7URF7WDtPfUBkxQ69yThQDPBANkm',
                platform_url='https://uvadlo-dev.instructure.com',
                auth_url='https://uvadlo-dev.instructure.com/api/lti/authorize_redirect',
                token_url='https://uvadlo-dev.instructure.com/login/oauth2/token',
                jwks_url='https://uvadlo-dev.instructure.com/api/lti/security/jwks'
            )
            print("LTI config created on Railway!")
    except Exception as e:
        print(f"LTI setup error: {e}")

# Run setup when app starts
with app.app_context():
    setup_lti_config()

# Routes
@app.route('/health')
def health_check():
    return {"status": "healthy", "timestamp": "2025-06-24"}, 200

@app.route('/debug/lti')
def debug_lti():
    import os
    import json
    
    debug_info = {}
    
    # Check if LTI config files exist
    lti_config_path = os.path.join(os.path.dirname(__file__), 'lti', 'config.json')
    jwks_path = os.path.join(os.path.dirname(__file__), 'lti', 'jwks.json')
    
    debug_info['lti_config_exists'] = os.path.exists(lti_config_path)
    debug_info['jwks_exists'] = os.path.exists(jwks_path)
    debug_info['lti_config_path'] = lti_config_path
    debug_info['jwks_path'] = jwks_path
    
    # Check environment variables
    debug_info['client_id'] = os.getenv('LTI_CLIENT_ID', 'NOT SET')
    debug_info['deployment_id'] = os.getenv('LTI_DEPLOYMENT_ID', 'NOT SET')
    
    # Try to read config if it exists
    if os.path.exists(lti_config_path):
        try:
            with open(lti_config_path, 'r') as f:
                debug_info['lti_config_content'] = json.load(f)
        except Exception as e:
            debug_info['lti_config_error'] = str(e)
    
    return debug_info

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