from canvasapi import Canvas
from canvasapi.exceptions import CanvasException
from app.config import Config
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class CanvasClient:
    def __init__(self, base_url: str = None, token: str = None):
        # Remove /api/v1 if present in the URL
        self.base_url = (base_url or Config.CANVAS_API_URL).replace('/api/v1', '')
        self.token = token or Config.CANVAS_API_TOKEN
        
        try:
            self.canvas = Canvas(self.base_url, self.token)
            # Test the connection
            self.current_user = self.canvas.get_current_user()
            logger.info(f"Connected to Canvas as {self.current_user.name}")
        except Exception as e:
            logger.error(f"Failed to connect to Canvas: {e}")
            raise
    
    def get_root_account(self) -> Dict:
        """Get the root account"""
        accounts = list(self.canvas.get_accounts())
        if accounts:
            root = accounts[0]  # Usually the first one is root
            return {
                'id': root.id,
                'name': root.name
            }
        raise Exception("No root account found")
    
    def create_subaccount(self, parent_id: int, name: str, **kwargs) -> Dict:
        """Create a new subaccount"""
        try:
            account = self.canvas.get_account(parent_id)
            subaccount = account.create_subaccount(
                account={'name': name, **kwargs}
            )
            return {
                'id': subaccount.id,
                'name': subaccount.name,
                'parent_account_id': subaccount.parent_account_id,
                'workflow_state': getattr(subaccount, 'workflow_state', 'active')
            }
        except CanvasException as e:
            logger.error(f"Failed to create subaccount: {e}")
            raise
    
    def create_course(self, account_id: int, name: str, course_code: str, **kwargs) -> Dict:
        """Create a new course"""
        try:
            account = self.canvas.get_account(account_id)
            
            # Set default values
            course_data = {
                'name': name,
                'course_code': course_code,
                'is_public': False,
                'is_public_to_auth_users': False,
                'workflow_state': 'available',  # Make course immediately available
                **kwargs
            }
            
            course = account.create_course(course=course_data)
            
            return {
                'id': course.id,
                'name': course.name,
                'course_code': course.course_code,
                'workflow_state': course.workflow_state
            }
        except CanvasException as e:
            logger.error(f"Failed to create course: {e}")
            raise
    
    def create_user(self, account_id: int, name: str, email: str, login_id: str, **kwargs) -> Dict:
        """Create a new user"""
        try:
            account = self.canvas.get_account(account_id)
            
            user_data = {
                'name': name,
                'short_name': name.split()[0],  # First name as short name
                'sortable_name': f"{name.split()[-1]}, {' '.join(name.split()[:-1])}",  # Last, First
                **kwargs
            }
            
            pseudonym_data = {
                'unique_id': login_id,
                'password': 'ChangeMePlease123!',  # Default password
                'sis_user_id': kwargs.get('sis_user_id'),
                'send_confirmation': False
            }
            
            user = account.create_user(
                user=user_data,
                pseudonym=pseudonym_data,
                communication_channel={'address': email, 'type': 'email'}
            )
            
            return {
                'id': user.id,
                'name': user.name,
                'email': email,
                'login_id': login_id
            }
        except CanvasException as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def enroll_user(self, course_id: int, user_id: int, role: str = "StudentEnrollment") -> Dict:
        """Enroll a user in a course"""
        try:
            course = self.canvas.get_course(course_id)
            enrollment = course.enroll_user(
                user_id,
                enrollment_type=role,
                enrollment_state='active'
            )
            
            return {
                'id': enrollment.id,
                'user_id': enrollment.user_id,
                'course_id': enrollment.course_id,
                'role': enrollment.role,
                'state': enrollment.enrollment_state
            }
        except CanvasException as e:
            logger.error(f"Failed to enroll user: {e}")
            raise
    
    def create_assignment(self, course_id: int, name: str, **kwargs) -> Dict:
        """Create an assignment in a course"""
        try:
            course = self.canvas.get_course(course_id)
            
            assignment_data = {
                'name': name,
                'submission_types': ['online_text_entry'],
                'points_possible': kwargs.get('points_possible', 100),
                'published': True,
                **kwargs
            }
            
            assignment = course.create_assignment(assignment=assignment_data)
            
            return {
                'id': assignment.id,
                'name': assignment.name,
                'points_possible': assignment.points_possible,
                'course_id': course_id
            }
        except CanvasException as e:
            logger.error(f"Failed to create assignment: {e}")
            raise
    
    def delete_course(self, course_id: int) -> Dict:
        """Delete a course"""
        try:
            course = self.canvas.get_course(course_id)
            course.delete()
            return {'success': True, 'course_id': course_id}
        except CanvasException as e:
            logger.error(f"Failed to delete course: {e}")
            raise
    
    def list_subaccounts(self, account_id: int) -> List[Dict]:
        """List all subaccounts"""
        try:
            account = self.canvas.get_account(account_id)
            subaccounts = []
            
            for sub in account.get_subaccounts(recursive=True):
                subaccounts.append({
                    'id': sub.id,
                    'name': sub.name,
                    'parent_account_id': sub.parent_account_id,
                    'workflow_state': getattr(sub, 'workflow_state', 'active')
                })
            
            return subaccounts
        except CanvasException as e:
            logger.error(f"Failed to list subaccounts: {e}")
            raise
    
    def get_account_courses(self, account_id: int, include_subaccounts: bool = True) -> List[Dict]:
        """Get all courses in an account"""
        try:
            account = self.canvas.get_account(account_id)
            courses = []
            
            # Get courses with additional info
            for course in account.get_courses(
                include=['term', 'teachers'],
                state=['available', 'completed', 'unpublished']
            ):
                courses.append({
                    'id': course.id,
                    'name': course.name,
                    'course_code': course.course_code,
                    'workflow_state': course.workflow_state,
                    'created_at': course.created_at,
                    'account_id': course.account_id
                })
            
            return courses
        except CanvasException as e:
            logger.error(f"Failed to get courses: {e}")
            raise
    
    def create_term(self, account_id: int, name: str, start_at: str, end_at: str) -> Dict:
        """Create an enrollment term"""
        try:
            account = self.canvas.get_account(account_id)
            
            # Note: Creating terms requires account admin permissions
            term = account.create_enrollment_term(
                enrollment_term={
                    'name': name,
                    'start_at': start_at,
                    'end_at': end_at
                }
            )
            
            return {
                'id': term.id,
                'name': term.name,
                'start_at': term.start_at,
                'end_at': term.end_at
            }
        except CanvasException as e:
            logger.error(f"Failed to create term: {e}")
            raise
    
    def get_environment_status(self, account_id: int = None) -> Dict:
        """Get status of the environment"""
        try:
            if not account_id:
                root = self.get_root_account()
                account_id = root['id']
            
            # Count subaccounts
            subaccounts = self.list_subaccounts(account_id)
            
            # Count courses
            courses = self.get_account_courses(account_id)
            
            # Get recent activity (last created course)
            last_activity = None
            if courses:
                # Sort by created_at and get the most recent
                sorted_courses = sorted(courses, key=lambda x: x.get('created_at', ''), reverse=True)
                if sorted_courses and sorted_courses[0].get('created_at'):
                    last_activity = sorted_courses[0]['created_at']
            
            return {
                'subaccounts': len(subaccounts),
                'courses': len(courses),
                'lastActivity': last_activity,
                'status': 'in-use' if (subaccounts or courses) else 'clean'
            }
        except Exception as e:
            logger.error(f"Failed to get environment status: {e}")
            raise