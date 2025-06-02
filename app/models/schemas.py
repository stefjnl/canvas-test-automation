from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SubAccount(BaseModel):
    name: str
    parent_account_id: Optional[int] = None
    sis_account_id: Optional[str] = None

class Course(BaseModel):
    name: str
    course_code: str
    account_id: int
    term_id: Optional[int] = None
    sis_course_id: Optional[str] = None
    
class User(BaseModel):
    name: str
    email: str
    login_id: str
    sis_user_id: Optional[str] = None
    
class Enrollment(BaseModel):
    user_id: int
    course_id: int
    role: str = Field(default="StudentEnrollment")
    section_id: Optional[int] = None

class TestEnvironmentConfig(BaseModel):
    environment: str
    subaccounts: List[Dict]
    courses: List[Dict]
    users: Optional[List[Dict]] = []
    enrollments: Optional[List[Dict]] = []

class CourseRequest(BaseModel):
    name: str
    sections: int = 1
    students: int = 0
    teachers: int = 1

class RequestOptions(BaseModel):
    configure_terms: bool = False
    add_apps: bool = False
    app_names: List[str] = []
    developer_keys: bool = False
    integration_accounts: bool = False

class TestEnvironmentRequest(BaseModel):
    scenario: str
    requester: str
    topdesk_number: Optional[str] = None
    environment: str
    jira_epic: Optional[str] = None
    start_date: str
    end_date: str
    admin_users: List[str]
    subaccount: Dict[str, Any]
    courses: List[CourseRequest]
    options: RequestOptions
    special_notes: Optional[str] = None