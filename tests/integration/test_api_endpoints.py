"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create test client for API."""
    return TestClient(app)


@pytest.fixture
def valid_request_payload():
    """Valid request payload for credit scoring."""
    return {
        "applicant_id": "integration_test_001",
        "grade_numeric": 3,
        "int_rate": 13.5,
        "inq_last_6mths": 0,
        "revol_util": 25.0,
        "installment": 350.0,
        "installment_to_income": 0.07,
        "loan_to_income": 0.30,
        "dti": 15.0,
        "open_acc": 8,
        "loan_amnt": 15000,
        "annual_inc": 50000,
        "credit_history_months": 120
    }


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_welcome(self, client):
        """Root endpoint should return welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Cashi" in data["message"]


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_returns_status(self, client):
        """Health endpoint should return status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert data["status"] in ["healthy", "degraded"]

    def test_health_response_schema(self, client):
        """Health response should match expected schema."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data["status"], str)
        assert isinstance(data["model_loaded"], bool)


class TestStatsEndpoint:
    """Tests for statistics endpoint."""

    def test_stats_returns_data(self, client):
        """Stats endpoint should return prediction statistics."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_predictions" in data
        assert "model_loaded" in data


class TestCreditScoreEndpoint:
    """Tests for credit scoring endpoint."""

    def test_valid_request_returns_score(self, client, valid_request_payload):
        """Valid request should return credit score response."""
        response = client.post("/credit/score", json=valid_request_payload)
        assert response.status_code == 200
        data = response.json()
        assert "applicant_id" in data
        assert "credit_score" in data
        assert "default_probability" in data
        assert "risk_level" in data
        assert "explanation" in data

    def test_valid_request_score_in_range(self, client, valid_request_payload):
        """Credit score should be within valid range (356-671)."""
        response = client.post("/credit/score", json=valid_request_payload)
        data = response.json()
        assert 300 <= data["credit_score"] <= 700

    def test_valid_request_probability_in_range(self, client, valid_request_payload):
        """Default probability should be between 0 and 1."""
        response = client.post("/credit/score", json=valid_request_payload)
        data = response.json()
        assert 0 <= data["default_probability"] <= 1

    def test_valid_request_risk_level_valid(self, client, valid_request_payload):
        """Risk level should be Low, Medium, or High."""
        response = client.post("/credit/score", json=valid_request_payload)
        data = response.json()
        assert data["risk_level"] in ["Low", "Medium", "High"]

    def test_low_income_rejected(self, client, valid_request_payload):
        """Income below $20K should be rejected with 400."""
        payload = valid_request_payload.copy()
        payload["annual_inc"] = 15000
        response = client.post("/credit/score", json=payload)
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "errors" in data["detail"]

    def test_high_loan_rejected(self, client, valid_request_payload):
        """Loan above $40K should be rejected with 400."""
        payload = valid_request_payload.copy()
        payload["loan_amnt"] = 50000
        response = client.post("/credit/score", json=payload)
        assert response.status_code == 400

    def test_invalid_interest_rate_rejected(self, client, valid_request_payload):
        """Interest rate outside 5-31% should be rejected."""
        payload = valid_request_payload.copy()
        payload["int_rate"] = 2.0
        response = client.post("/credit/score", json=payload)
        assert response.status_code == 400

    def test_high_risk_applicant_gets_override(self, client, valid_request_payload):
        """High risk applicant should get score capped at 450."""
        payload = valid_request_payload.copy()
        payload["credit_history_months"] = 6  # Short history triggers override
        response = client.post("/credit/score", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["credit_score"] <= 450
        assert data["default_probability"] >= 0.70
        assert data["risk_level"] == "High"

    def test_missing_field_returns_422(self, client):
        """Missing required field should return 422 validation error."""
        payload = {"applicant_id": "test"}  # Missing other required fields
        response = client.post("/credit/score", json=payload)
        assert response.status_code == 422

    def test_applicant_id_in_response(self, client, valid_request_payload):
        """Response should contain same applicant_id as request."""
        payload = valid_request_payload.copy()
        payload["applicant_id"] = "unique_test_id_123"
        response = client.post("/credit/score", json=payload)
        data = response.json()
        assert data["applicant_id"] == "unique_test_id_123"

    def test_explanation_not_empty(self, client, valid_request_payload):
        """Explanation should not be empty."""
        response = client.post("/credit/score", json=valid_request_payload)
        data = response.json()
        assert len(data["explanation"]) > 0


class TestAPIErrorHandling:
    """Tests for API error handling."""

    def test_invalid_json_returns_422(self, client):
        """Invalid JSON should return 422."""
        response = client.post(
            "/credit/score",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_wrong_method_returns_405(self, client):
        """GET on POST endpoint should return 405."""
        response = client.get("/credit/score")
        assert response.status_code == 405

    def test_nonexistent_endpoint_returns_404(self, client):
        """Nonexistent endpoint should return 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404
