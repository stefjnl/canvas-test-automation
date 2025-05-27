from pydantic import BaseModel, Field
from typing import List, Optional, Dict
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