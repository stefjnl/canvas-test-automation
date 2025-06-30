from flask import Blueprint, request, jsonify, render_template, session, url_for
from pylti1p3.contrib.flask import FlaskOIDCLogin, FlaskMessageLaunch, FlaskRequest, FlaskCacheDataStorage
from pylti1p3.deep_link import DeepLink
from pylti1p3.grade import Grade
from pylti1p3.lineitem import LineItem
from pylti1p3.exception import LtiException
import json
import os

from app.lti.config import LTIConfig

lti_bp = Blueprint('lti', __name__, url_prefix='/lti')

def get_launch_data_storage():
    return FlaskCacheDataStorage(cache=session)

def get_jwks():
    """Serve the public JWKS for Canvas to verify our signatures"""
    jwks_path = os.path.join(os.path.dirname(__file__), 'jwks.json')
    with open(jwks_path, 'r') as f:
        return json.load(f)

@lti_bp.route('/jwks', methods=['GET'])
def jwks():
    """JWKS endpoint for Canvas to fetch our public keys"""
    return jsonify(get_jwks())

@lti_bp.route('/config', methods=['GET'])
def config():
    """LTI configuration JSON for Canvas"""
    config = {
        "title": "Canvas Test Automation Tool",
        "description": "Automated test environment setup for Canvas",
        "oidc_initiation_url": url_for('lti.login', _external=True, _scheme='https'),
        "target_link_uri": url_for('lti.launch', _external=True, _scheme='https'),
        "scopes": [
            "https://purl.imsglobal.org/spec/lti/scope/lineitem",
            "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
            "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
            "https://purl.imsglobal.org/spec/lti-ags/scope/score",
            "https://canvas.instructure.com/lti/public_jwk/scope/update",
            "https://canvas.instructure.com/lti/account_navigation/scope/show",
            "https://canvas.instructure.com/lti/feature_flags/scope/show"
        ],
        "extensions": [{
            "platform": "canvas.instructure.com",
            "settings": {
                "platform": "canvas.instructure.com",
                "placements": [{
                    "placement": "account_navigation",
                    "message_type": "LtiResourceLinkRequest",
                    "text": "Test Automation",
                    "enabled": True,
                    "icon_url": url_for('static', filename='icon.png', _external=True, _scheme='https'),
                    "target_link_uri": url_for('lti.launch', _external=True, _scheme='https'),
                    "canvas_icon_class": "icon-lti"
                }]
            },
            "privacy_level": "public"
        }],
        "public_jwk_url": url_for('lti.jwks', _external=True, _scheme='https'),
        "custom_fields": {
            "canvas_user_id": "$Canvas.user.id",
            "canvas_user_name": "$Person.name.full",
            "canvas_user_email": "$Person.email.primary",
            "canvas_account_id": "$Canvas.account.id",
            "canvas_account_name": "$Canvas.account.name"
        }
    }
    return jsonify(config)

@lti_bp.route('/login', methods=['GET', 'POST'])
def login():
    """LTI 1.3 login initiation"""
    tool_conf = LTIConfig.create_tool_conf()
    launch_data_storage = get_launch_data_storage()
    flask_request = FlaskRequest()
    
    oidc_login = FlaskOIDCLogin(
        flask_request,
        tool_conf,
        launch_data_storage=launch_data_storage
    )
    
    try:
        target_link_uri = url_for('lti.launch', _external=True, _scheme='https')
        return oidc_login.enable_check_cookies().redirect(target_link_uri)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@lti_bp.route('/launch', methods=['POST'])
def launch():
    """LTI 1.3 tool launch"""
    tool_conf = LTIConfig.create_tool_conf()
    launch_data_storage = get_launch_data_storage()
    flask_request = FlaskRequest()
    
    message_launch = FlaskMessageLaunch(
        flask_request,
        tool_conf,
        launch_data_storage=launch_data_storage
    )
    
    try:
        message_launch = message_launch.validate()
        
        # Get launch data
        launch_data = message_launch.get_launch_data()
        
        # Store user info in session
        session['lti_launch'] = True
        session['canvas_user_id'] = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {}).get('canvas_user_id')
        session['canvas_user_name'] = launch_data.get('name', 'Unknown User')
        session['canvas_user_email'] = launch_data.get('email', '')
        session['canvas_account_id'] = launch_data.get('https://purl.imsglobal.org/spec/lti/claim/custom', {}).get('canvas_account_id')
        session['is_instructor'] = 'http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor' in launch_data.get('https://purl.imsglobal.org/spec/lti/claim/roles', [])
        
        # Redirect to main app
        return render_template('lti_launch.html', 
                             user_name=session['canvas_user_name'],
                             is_instructor=session['is_instructor'])
        
    except LtiException as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Launch failed: {str(e)}"}), 500

@lti_bp.route('/close', methods=['GET'])
def close():
    """Close the LTI tool and return to Canvas"""
    session.clear()
    return render_template('lti_close.html')

@lti_bp.route('/login', methods=['GET', 'POST'])
def login():
    """LTI 1.3 login initiation with debugging"""
    print("=== CANVAS LOGIN REQUEST ===")
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Args: {dict(request.args)}")
    print(f"Form: {dict(request.form)}")
    print(f"Headers: {dict(request.headers)}")
    
    # Check what issuer Canvas is sending
    iss = request.args.get('iss') or request.form.get('iss')
    print(f"Canvas Issuer (iss): {iss}")
    print(f"Our Platform URL: {os.getenv('CANVAS_PLATFORM_URL')}")
    print("============================")
    
    try:
        tool_conf = LTIConfig.create_tool_conf()
        launch_data_storage = get_launch_data_storage()
        flask_request = FlaskRequest()
        
        oidc_login = FlaskOIDCLogin(
            flask_request,
            tool_conf,
            launch_data_storage=launch_data_storage
        )
        
        target_link_uri = url_for('lti.launch', _external=True, _scheme='https')
        return oidc_login.enable_check_cookies().redirect(target_link_uri)
        
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({"error": str(e), "canvas_issuer": iss, "our_platform": os.getenv('CANVAS_PLATFORM_URL')}), 400