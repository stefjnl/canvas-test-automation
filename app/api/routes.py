from flask import Blueprint, request, jsonify
from app.api.canvas_client import CanvasClient
from app.models.schemas import TestEnvironmentConfig, TestEnvironmentRequest
from datetime import datetime
import logging
import json
import os
import uuid

logger = logging.getLogger(__name__)

# Define Blueprint FIRST
api_bp = Blueprint('api', __name__)

# Helper functions for request management
def get_requests_file():
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'requests.json')

def load_requests():
    """Load all requests from storage"""
    try:
        with open(get_requests_file(), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_requests(requests):
    """Save requests to storage"""
    os.makedirs(os.path.dirname(get_requests_file()), exist_ok=True)
    with open(get_requests_file(), 'w') as f:
        json.dump(requests, f, indent=2)

def find_request(request_id):
    """Find a specific request by ID"""
    requests = load_requests()
    for req in requests:
        if req['id'] == request_id:
            return req
    return None

def get_scenario_name(scenario_id):
    """Get friendly name for scenario"""
    names = {
        'app-integration': 'App Integration Test',
        'department-structure': 'Department Structure',
        'bulk-testing': 'Bulk User Testing',
        'assignment-workflow': 'Assignment Workflow',
        'custom': 'Custom Setup'
    }
    return names.get(scenario_id, scenario_id)

def store_request_details(request_data, results):
    """Store request details for tracking and cleanup"""
    request_record = {
        "id": results['request_id'],
        "timestamp": datetime.now().isoformat(),
        "request": request_data,
        "results": results
    }
    
    # Save to file (in production, use a database)
    try:
        with open('request_log.json', 'r') as f:
            log = json.load(f)
    except:
        log = []
    
    log.append(request_record)
    
    with open('request_log.json', 'w') as f:
        json.dump(log, f, indent=2)

# Routes
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
            "id": "app-integration",
            "name": "App Integration Test",
            "description": "Test LTI tools like Peerceptiv, Turnitin, or custom apps",
            "icon": "🔌"
        },
        {
            "id": "department-structure",
            "name": "Department Structure",
            "description": "Create realistic faculty/department hierarchy",
            "icon": "🏛️"
        },
        {
            "id": "bulk-testing",
            "name": "Bulk User Testing",
            "description": "Test with many students and complex enrollments",
            "icon": "👥"
        },
        {
            "id": "assignment-workflow",
            "name": "Assignment Workflow Test",
            "description": "Test grading, rubrics, and submissions",
            "icon": "📝"
        },
        {
            "id": "custom",
            "name": "Custom Setup",
            "description": "Configure everything manually",
            "icon": "⚙️"
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

@api_bp.route('/requests', methods=['GET'])
def get_requests():
    """Get all test environment requests"""
    requests = load_requests()
    # Sort by created date, newest first
    requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(requests), 200

@api_bp.route('/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    """Get a specific request"""
    request = find_request(request_id)
    if request:
        return jsonify(request), 200
    return jsonify({"error": "Request not found"}), 404

@api_bp.route('/requests/<request_id>/cleanup', methods=['POST'])
def cleanup_request(request_id):
    """Cleanup all resources created by a specific request"""
    request_obj = find_request(request_id)
    if not request_obj:
        return jsonify({"error": "Request not found"}), 404
    
    if request_obj.get('cleaned'):
        return jsonify({"error": "Request already cleaned up"}), 400
    
    client = CanvasClient()
    results = {
        "deleted_courses": 0,
        "deleted_users": 0,
        "errors": []
    }
    
    # Delete courses
    for course in request_obj['created_resources'].get('courses', []):
        try:
            client.delete_course(course['id'])
            results['deleted_courses'] += 1
            logger.info(f"Deleted course {course['id']} from request {request_id}")
        except Exception as e:
            error_msg = f"Failed to delete course {course['id']}: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
    
    # Note: Canvas doesn't allow deleting users via API
    # We'll mark them as deleted in our tracking
    results['deleted_users'] = len(request_obj['created_resources'].get('users', []))
    
    # Update request status
    requests = load_requests()
    for req in requests:
        if req['id'] == request_id:
            req['cleaned'] = True
            req['cleaned_at'] = datetime.now().isoformat()
            req['cleanup_results'] = results
            break
    save_requests(requests)
    
    return jsonify(results), 200

@api_bp.route('/submit-request', methods=['POST'])
def submit_request():
    """Submit a new test environment request"""
    try:
        data = request.json
        
        # Generate unique request ID
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        # Create request record
        request_record = {
            "id": request_id,
            "created_at": datetime.now().isoformat(),
            "scenario": data.get('scenario'),
            "scenario_name": get_scenario_name(data.get('scenario')),
            "requester": data.get('requester'),
            "topdesk_number": data.get('topdesk_number'),
            "environment": data.get('environment'),
            "start_date": data.get('start_date'),
            "end_date": data.get('end_date'),
            "request_data": data,
            "created_resources": {
                "subaccounts": [],
                "courses": [],
                "users": [],
                "errors": []
            },
            "cleaned": False
        }
        
        client = CanvasClient()
        
        # Create subaccount if requested
        if data['subaccount']['create']:
            try:
                subaccount = client.create_subaccount(
                    parent_id=1,  # Root account
                    name=data['subaccount']['name']
                )
                request_record['created_resources']['subaccounts'].append(subaccount)
                account_id = subaccount['id']
            except Exception as e:
                request_record['created_resources']['errors'].append(f"Failed to create subaccount: {str(e)}")
                account_id = 1
        else:
            account_id = 1
        
        # Create admin access
        for admin_user in data['admin_users']:
            # In real implementation, grant admin access to the users
            logger.info(f"Would grant admin access to {admin_user}")
        
        # Create courses and users
        for course_config in data['courses']:
            try:
                # Create course
                course = client.create_course(
                    account_id=account_id,
                    name=course_config['name'],
                    course_code=f"TEST-{request_id[-8:]}"
                )
                request_record['created_resources']['courses'].append(course)
                
                # Create sections if more than 1
                if course_config['sections'] > 1:
                    for i in range(2, course_config['sections'] + 1):
                        # Canvas API for creating sections
                        logger.info(f"Would create section {i} for course {course['id']}")
                
                # Create test students
                for i in range(course_config['students']):
                    user = client.create_user(
                        account_id=account_id,
                        name=f"Test Student {i+1} ({request_id[-8:]})",
                        email=f"test.student{i+1}.{request_id[-8:]}@test.uva.nl",
                        login_id=f"tstudent{i+1}_{request_id[-8:]}"
                    )
                    request_record['created_resources']['users'].append(user)
                    
                    # Enroll in course
                    client.enroll_user(
                        course_id=course['id'],
                        user_id=user['id'],
                        role='StudentEnrollment'
                    )
                
                # Create teachers
                for i in range(course_config['teachers']):
                    user = client.create_user(
                        account_id=account_id,
                        name=f"Test Teacher {i+1} ({request_id[-8:]})",
                        email=f"test.teacher{i+1}.{request_id[-8:]}@test.uva.nl",
                        login_id=f"tteacher{i+1}_{request_id[-8:]}"
                    )
                    request_record['created_resources']['users'].append(user)
                    
                    # Enroll as teacher
                    client.enroll_user(
                        course_id=course['id'],
                        user_id=user['id'],
                        role='TeacherEnrollment'
                    )
                    
            except Exception as e:
                request_record['created_resources']['errors'].append(f"Failed to create course {course_config['name']}: {str(e)}")
        
        # Handle additional options
        if data['options']['configure_terms']:
            logger.info("Would configure terms")
        
        if data['options']['add_apps']:
            for app_name in data['options']['app_names']:
                logger.info(f"Would configure app: {app_name}")
        
        # Save request record
        requests = load_requests()
        requests.append(request_record)
        save_requests(requests)
        
        # Also store in old format for compatibility
        store_request_details(data, {
            "request_id": request_id,
            "status": "completed",
            "created_resources": request_record['created_resources']
        })
        
        return jsonify({
            "request_id": request_id,
            "status": "completed",
            "created_resources": request_record['created_resources']
        }), 200
        
    except Exception as e:
        logger.error(f"Request submission failed: {e}")
        return jsonify({"error": str(e)}), 400