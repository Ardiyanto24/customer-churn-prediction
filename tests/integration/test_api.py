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


# ---------------------------------------------------------------------------
# Task 5.1.2 — degraded_api_client fixture + TestHealthDegraded
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def degraded_api_client(dummy_model, dummy_preprocessor):
    """
    FastAPI TestClient where predictor._is_ready is False, simulating a
    failed artifact load (degraded mode). model and preprocessor are not
    injected so the API behaves as if startup failed.
    """
    from unittest.mock import patch
    from api.main import app
    from api.predictor import predictor

    with TestClient(app) as client:
        # Override to degraded state (lifespan already tried and failed)
        predictor._model = None
        predictor._preprocessor = None
        predictor._is_ready = False
        predictor._model_version = "unknown"
        yield client

    # Ensure clean state after test
    predictor._model = None
    predictor._preprocessor = None
    predictor._is_ready = False
    predictor._model_version = "unknown"


from starlette.testclient import TestClient  # noqa: E402 — needed for local fixture


class TestHealthDegraded:
    """Tests for /health endpoint when the model is not ready (degraded mode)."""

    def test_health_returns_degraded_when_model_not_loaded(
        self, degraded_api_client
    ):
        """
        GET /health must return HTTP 200 (not 503) even in degraded mode so
        that load balancers know the application process is alive.
        The response body must show status='degraded' and model_loaded=False.
        """
        response = degraded_api_client.get("/health")

        assert response.status_code == 200, (
            f"Health endpoint should return 200 even in degraded mode, "
            f"got {response.status_code}"
        )
        body = response.json()
        assert body["status"] == "degraded", (
            f"Expected status='degraded': {body}"
        )
        assert body["model_loaded"] is False, (
            f"Expected model_loaded=False in degraded mode: {body}"
        )
