# Canvas Test Automation Tool

A web application for managing Canvas LMS test environments at UvA DLO.

## Features

- Create and manage subaccount structures
- Set up test courses
- Create test users and enrollments
- Clean up test environments
- Support for multiple test environments (Acceptatie, TES, Development)
- Etc.

## Setup

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your Canvas API credentials
6. Run the application: `python run.py`

## Development

The application is built with:
- Flask (Python web framework)
- Canvas API integration
- Pydantic for data validation
- Simple HTML/CSS/JS frontend

## Testing

Run tests with: `pytest`

## Authors

UvA DLO: S.J. Slagter