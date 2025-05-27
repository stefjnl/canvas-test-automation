from flask import Flask, render_template
from flask_cors import CORS
from app.api.routes import api_bp
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading template: {str(e)}<br>Looking in: {app.template_folder}"

@app.errorhandler(404)
def not_found(error):
    return {"error": "Resource not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500