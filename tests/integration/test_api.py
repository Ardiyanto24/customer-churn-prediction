# tests/integration/test_api.py
#
# Integration tests for the FastAPI service (api/main.py).
#
# All tests use FastAPI TestClient — no real server needed.
# The predictor singleton is injected with a dummy model + preprocessor
# via the api_client fixture defined in tests/conftest.py.
# SHAP computation is mocked so tests remain fast and deterministic.

import io

import pytest

# Mark every test in this module as an integration test
pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Task 5.1.1 — TestBaseEndpoints
# ---------------------------------------------------------------------------

class TestBaseEndpoints:
    """Tests for root (/) and health (/health) endpoints."""

    def test_root_endpoint_returns_200_with_navigation_info(self, api_client):
        """GET / must return 200 with at least 'docs' and 'health' navigation keys."""
        response = api_client.get("/")

        assert response.status_code == 200
        body = response.json()
        assert "docs" in body, f"Expected 'docs' key in root response: {body}"
        assert "health" in body, f"Expected 'health' key in root response: {body}"

    def test_health_endpoint_returns_healthy_when_model_loaded(self, api_client):
        """
        GET /health must return 200 with status='healthy', model_loaded=True,
        and uptime_seconds > 0 when the dummy model is injected.
        """
        response = api_client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy", f"Expected status='healthy': {body}"
        assert body["model_loaded"] is True, f"Expected model_loaded=True: {body}"
        assert isinstance(body["uptime_seconds"], float), (
            f"Expected uptime_seconds to be float: {body}"
        )
        assert body["uptime_seconds"] > 0, (
            f"Expected uptime_seconds > 0: {body}"
        )
