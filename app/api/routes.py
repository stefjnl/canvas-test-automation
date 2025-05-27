from flask import Blueprint, request, jsonify
from app.api.canvas_client import CanvasClient
from app.models.schemas import TestEnvironmentConfig

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@api_bp.route('/environments', methods=['GET'])
def get_environments():
    """Get available test environments"""
    from app.config import Config
    return jsonify(Config.TEST_ENVIRONMENTS), 200

@api_bp.route('/setup', methods=['POST'])
def setup_environment():
    """Set up a test environment based on configuration"""
    try:
        config = TestEnvironmentConfig(**request.json)
        client = CanvasClient()
        
        results = {
            "subaccounts": [],
            "courses": [],
            "errors": []
        }
        
        # Create subaccounts
        for subaccount in config.subaccounts:
            try:
                parent_id = subaccount.pop('parent_account_id', 1)
                name = subaccount.pop('name')

                result = client.create_subaccount(parent_id, name, **subaccount)
                results["subaccounts"].append(result)
            except Exception as e:
                results["errors"].append(f"Failed to create subaccount: {str(e)}")
        
        # Create courses
        for course in config.courses:
            try:
                result = client.create_course(**course)
                results["courses"].append(result)
            except Exception as e:
                results["errors"].append(f"Failed to create course: {str(e)}")
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/cleanup', methods=['POST'])
def cleanup_environment():
    """Clean up test environment"""
    try:
        data = request.json
        client = CanvasClient()
        
        results = {
            "deleted_courses": [],
            "errors": []
        }
        
        # Delete courses
        for course_id in data.get('course_ids', []):
            try:
                client.delete_course(course_id)
                results["deleted_courses"].append(course_id)
            except Exception as e:
                results["errors"].append(f"Failed to delete course {course_id}: {str(e)}")
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@api_bp.route('/environments/<env>/status', methods=['GET'])
def get_environment_status(env):
    """Get status of a specific environment"""
    try:
        # TODO: Implement actual Canvas API calls to check status
        # For now, return mock data
        return jsonify({
            "environment": env,
            "subaccounts": 0,
            "courses": 0,
            "lastActivity": None,
            "status": "clean"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400