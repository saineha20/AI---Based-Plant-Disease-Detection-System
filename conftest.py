# conftest.py
import sys
import os
import pytest

# Add root directory to sys.path so tests can import app and backend modules directly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
