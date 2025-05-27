import requests
from typing import Dict, List, Optional
from app.config import Config

class CanvasClient:
    def __init__(self, base_url: str = None, token: str = None):
        self.base_url = base_url or Config.CANVAS_API_URL
        self.token = token or Config.CANVAS_API_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def create_subaccount(self, parent_id: int, name: str, **kwargs) -> Dict:
        """Create a new subaccount"""
        url = f"{self.base_url}/accounts/{parent_id}/sub_accounts"
        data = {
            'account': {
                'name': name,
                **kwargs
            }
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_course(self, account_id: int, name: str, course_code: str, **kwargs) -> Dict:
        """Create a new course"""
        url = f"{self.base_url}/accounts/{account_id}/courses"
        data = {
            'course': {
                'name': name,
                'course_code': course_code,
                **kwargs
            }
        }
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def delete_course(self, course_id: int) -> Dict:
        """Delete a course"""
        url = f"{self.base_url}/courses/{course_id}"
        data = {'event': 'delete'}
        response = requests.delete(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def list_subaccounts(self, account_id: int) -> List[Dict]:
        """List all subaccounts"""
        url = f"{self.base_url}/accounts/{account_id}/sub_accounts"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()