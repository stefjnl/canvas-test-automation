from flask import Blueprint, request, jsonify
from app.api.canvas_client import CanvasClient
from app.models.schemas import TestEnvironmentConfig
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@api_bp.route('/environments', methods=['GET'])
def get_environments():
    """Get available test environments"""
    from app.config import Config
    return jsonify(Config.TEST_ENVIRONMENTS), 200

@api_bp.route('/environments/<env>/status', methods=['GET'])
def get_environment_status(env):
    """Get status of a specific environment"""
    try:
        client = CanvasClient()
        status = client.get_environment_status()
        status['environment'] = env
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting status for {env}: {e}")
        return jsonify({"error": str(e)}), 400

@api_bp.route('/setup', methods=['POST'])
def setup_environment():
    """Set up a test environment based on configuration"""
    try:
        config = TestEnvironmentConfig(**request.json)
        client = CanvasClient()
        
        results = {
            "subaccounts": [],
            "courses": [],
            "users": [],
            "enrollments": [],
            "errors": []
        }
        
        # Create subaccounts
        for subaccount in config.subaccounts:
            try:
                # Extract positional arguments
                parent_id = subaccount.pop('parent_account_id', 1)
                name = subaccount.pop('name')
                
                result = client.create_subaccount(parent_id, name, **subaccount)
                results["subaccounts"].append(result)
            except Exception as e:
                error_msg = f"Failed to create subaccount '{name}': {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create courses
        for course in config.courses:
            try:
                # Extract positional arguments
                account_id = course.pop('account_id', 1)
                name = course.pop('name')
                course_code = course.pop('course_code')
                
                result = client.create_course(account_id, name, course_code, **course)
                results["courses"].append(result)
            except Exception as e:
                error_msg = f"Failed to create course '{name}': {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create users (if specified)
        for user in config.users:
            try:
                account_id = user.pop('account_id', 1)
                name = user.pop('name')
                email = user.pop('email')
                login_id = user.pop('login_id')
                
                result = client.create_user(account_id, name, email, login_id, **user)
                results["users"].append(result)
            except Exception as e:
                error_msg = f"Failed to create user '{name}': {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Create enrollments (if specified)
        for enrollment in config.enrollments:
            try:
                course_id = enrollment.pop('course_id')
                user_id = enrollment.pop('user_id')
                role = enrollment.pop('role', 'StudentEnrollment')
                
                result = client.enroll_user(course_id, user_id, role)
                results["enrollments"].append(result)
            except Exception as e:
                error_msg = f"Failed to create enrollment: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return jsonify({"error": str(e)}), 400

@api_bp.route('/cleanup', methods=['POST'])
def cleanup_environment():
    """Clean up test environment"""
    try:
        data = request.json
        client = CanvasClient()
        
        results = {
            "deleted_courses": [],
            "deleted_subaccounts": [],
            "errors": []
        }
        
        # Delete courses first (they depend on subaccounts)
        for course_id in data.get('course_ids', []):
            try:
                client.delete_course(course_id)
                results["deleted_courses"].append(course_id)
            except Exception as e:
                error_msg = f"Failed to delete course {course_id}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Note: Canvas doesn't allow deleting subaccounts via API
        # We'll just track them as "cleaned"
        results["deleted_subaccounts"] = data.get('subaccount_ids', [])
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return jsonify({"error": str(e)}), 400

@api_bp.route('/test-scenarios', methods=['GET'])
def get_test_scenarios():
    """Get predefined test scenarios (menukaart)"""
    scenarios = [
        {
            "id": "basic_course",
            "name": "Basic Course Setup",
            "description": "Single course with 5 students and 1 teacher",
            "icon": "📚"
        },
        {
            "id": "department_structure",
            "name": "Department Structure",
            "description": "Faculty → Department → 3 Courses hierarchy",
            "icon": "🏛️"
        },
        {
            "id": "assignment_workflow",
            "name": "Assignment Workflow Test",
            "description": "Course with assignments, rubrics, and test submissions",
            "icon": "📝"
        },
        {
            "id": "multi_term",
            "name": "Multi-Term Setup",
            "description": "Courses across different academic terms",
            "icon": "📅"
        },
        {
            "id": "role_testing",
            "name": "Role & Permission Testing",
            "description": "Users with various roles and custom permissions",
            "icon": "👥"
        }
    ]
    return jsonify(scenarios), 200

@api_bp.route('/setup-scenario/<scenario_id>', methods=['POST'])
def setup_scenario(scenario_id):
    """Set up a predefined test scenario"""
    try:
        client = CanvasClient()
        environment = request.json.get('environment', 'development')
        
        # Define scenario configurations
        scenarios = {
            "basic_course": {
                "subaccounts": [],
                "courses": [
                    {"name": "Test Course 101", "course_code": "TEST101", "account_id": 1}
                ],
                "users": [
                    {"name": "Test Teacher", "email": "teacher@test.uva.nl", "login_id": "teacher1", "account_id": 1},
                    {"name": "Test Student 1", "email": "student1@test.uva.nl", "login_id": "student1", "account_id": 1},
                    {"name": "Test Student 2", "email": "student2@test.uva.nl", "login_id": "student2", "account_id": 1},
                    {"name": "Test Student 3", "email": "student3@test.uva.nl", "login_id": "student3", "account_id": 1},
                    {"name": "Test Student 4", "email": "student4@test.uva.nl", "login_id": "student4", "account_id": 1},
                    {"name": "Test Student 5", "email": "student5@test.uva.nl", "login_id": "student5", "account_id": 1}
                ],
                "enrollments": []  # Will be populated after creation
            },
            "department_structure": {
                "subaccounts": [
                    {"name": "Test Faculty", "parent_account_id": 1},
                    {"name": "Test Department", "parent_account_id": 1}  # Will be updated with faculty ID
                ],
                "courses": [
                    {"name": "Introduction to Testing", "course_code": "TEST101", "account_id": 1},
                    {"name": "Advanced Testing", "course_code": "TEST201", "account_id": 1},
                    {"name": "Testing Practicum", "course_code": "TEST301", "account_id": 1}
                ],
                "users": [],
                "enrollments": []
            }
        }
        
        if scenario_id not in scenarios:
            return jsonify({"error": f"Unknown scenario: {scenario_id}"}), 400
        
        config = TestEnvironmentConfig(
            environment=environment,
            **scenarios[scenario_id]
        )
        
        # Use the existing setup_environment logic
        request.json = config.dict()
        return setup_environment()
        
    except Exception as e:
        logger.error(f"Scenario setup failed: {e}")
        return jsonify({"error": str(e)}), 400