"""
Basic tests for Payment Service
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Payment Service"
    assert data["status"] == "running"

def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/api/payments/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "payment-service"

# Note: Authentication tests would require valid JWT tokens
# Integration tests would require database setup
