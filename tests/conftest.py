"""
Pytest configuration and fixtures for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


import app as app_module

@pytest.fixture
def clean_activities(client):
    """Reset activities to a clean state before each test"""
    # Get the app instance and reset participants
    for activity in app_module.activities.values():
        activity["participants"] = []
    
    # Reset Chess Club and Programming Class to their original participants
    app_module.activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu"
    ]
    app_module.activities["Programming Class"]["participants"] = [
        "emma@mergington.edu",
        "sophia@mergington.edu"
    ]
    app_module.activities["Gym Class"]["participants"] = [
        "john@mergington.edu",
        "olivia@mergington.edu"
    ]
    
    yield client
    
    # Cleanup after test
    for activity in app_module.activities.values():
        activity["participants"] = []
    app_module.activities["Chess Club"]["participants"] = [
        "michael@mergington.edu",
        "daniel@mergington.edu"
    ]
    app_module.activities["Programming Class"]["participants"] = [
        "emma@mergington.edu",
        "sophia@mergington.edu"
    ]
    app_module.activities["Gym Class"]["participants"] = [
        "john@mergington.edu",
        "olivia@mergington.edu"
    ]
