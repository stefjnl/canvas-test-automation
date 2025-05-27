from flask import Flask, render_template, request
from flask_cors import CORS
from app.api.routes import api_bp
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/setup')
def setup():
    # Get environment from query parameter
    env = request.args.get('env', '')
    return render_template('index.html', selected_env=env)

@app.errorhandler(404)
def not_found(error):
    return {"error": "Resource not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500