from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from app.api.routes import api_bp
from app.config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

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