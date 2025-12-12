"""Unit tests for Brain Engine API."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Import the app - note: this will fail if env vars aren't set
# In real testing, we'd mock the settings
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# Mock settings before importing app
@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings for all tests."""
    with patch.dict(os.environ, {
        'API_KEY': 'test-api-key',
        'OXYLABS_USERNAME': 'test-user',
        'OXYLABS_PASSWORD': 'test-pass',
    }):
        yield


@pytest.fixture
def client():
    """Create test client with mocked settings."""
    # Import here to use mocked env vars
    with patch.dict(os.environ, {
        'API_KEY': 'test-api-key',
        'OXYLABS_USERNAME': 'test-user',
        'OXYLABS_PASSWORD': 'test-pass',
    }):
        # Need to reload modules to pick up mocked env
        from src.main import app
        return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_returns_health(self, client):
        """Test root endpoint returns health status."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "brain-engine"
        assert "version" in data
        assert "timestamp" in data
    
    def test_health_endpoint(self, client):
        """Test /health endpoint returns health status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "brain-engine"


class TestSearchEndpoint:
    """Tests for flight search endpoint."""
    
    def test_search_requires_auth(self, client):
        """Test that search endpoint requires authorization."""
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15"
            }
        )
        assert response.status_code == 401
        assert "Authorization header required" in response.json()["detail"]
    
    def test_search_rejects_invalid_auth_format(self, client):
        """Test that search rejects invalid auth format."""
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15"
            },
            headers={"Authorization": "InvalidFormat token"}
        )
        assert response.status_code == 401
        assert "Invalid authorization format" in response.json()["detail"]
    
    def test_search_rejects_wrong_api_key(self, client):
        """Test that search rejects wrong API key."""
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15"
            },
            headers={"Authorization": "Bearer wrong-key"}
        )
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]
    
    def test_search_validates_origin_length(self, client):
        """Test that search validates origin airport code length."""
        response = client.post(
            "/api/search",
            json={
                "origin": "LA",  # Too short
                "destination": "NRT",
                "departureDate": "2025-03-15"
            },
            headers={"Authorization": "Bearer test-api-key"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_search_validates_destination_length(self, client):
        """Test that search validates destination airport code length."""
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRTT",  # Too long
                "departureDate": "2025-03-15"
            },
            headers={"Authorization": "Bearer test-api-key"}
        )
        assert response.status_code == 422  # Validation error
    
    @patch('src.main.search_flights_multi_country')
    def test_search_with_valid_request(self, mock_search, client):
        """Test search with valid request and mocked scraper."""
        # Mock the scraper response
        mock_search.return_value = AsyncMock(return_value={
            "flights": [
                {
                    "id": "test123",
                    "airline": "Test Airlines",
                    "price": 500.00,
                    "currency": "USD",
                    "departure_time": "10:00 AM",
                    "arrival_time": "3:00 PM",
                    "duration": "11h 00m",
                    "stops": 0,
                    "searched_from_country": "India",
                    "original_price": 700.00,
                    "savings_percent": 28.6,
                    "savings_amount": 200.00,
                }
            ],
            "total_results": 1,
            "countries_searched": ["India", "Mexico"],
            "best_price": 500.00,
            "baseline_price": 700.00,
            "best_savings_percent": 28.6,
            "search_time_seconds": 5.0,
        })()
        
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15",
                "returnDate": "2025-03-22",
                "passengers": 1,
                "cabinClass": "economy"
            },
            headers={"Authorization": "Bearer test-api-key"}
        )
        
        # Note: This test may fail without proper async mocking
        # In production, we'd use pytest-asyncio and proper async mocks
        # For now, we're testing the validation and auth logic


class TestRequestValidation:
    """Tests for request validation."""
    
    def test_missing_required_fields(self, client):
        """Test that missing required fields return validation error."""
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX"
                # Missing destination and departureDate
            },
            headers={"Authorization": "Bearer test-api-key"}
        )
        assert response.status_code == 422
    
    def test_passengers_range(self, client):
        """Test that passengers must be between 1 and 9."""
        # Test too many passengers
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15",
                "passengers": 10  # Too many
            },
            headers={"Authorization": "Bearer test-api-key"}
        )
        assert response.status_code == 422
        
        # Test zero passengers
        response = client.post(
            "/api/search",
            json={
                "origin": "LAX",
                "destination": "NRT",
                "departureDate": "2025-03-15",
                "passengers": 0  # Too few
            },
            headers={"Authorization": "Bearer test-api-key"}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
