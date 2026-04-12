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


# ---------------------------------------------------------------------------
# Task 5.2.1 — TestPredictEndpoint
# ---------------------------------------------------------------------------

class TestPredictEndpoint:
    """Tests for POST /predict endpoint with a ready model."""

    def test_predict_returns_200_with_valid_input(self, api_client, sample_raw_row):
        """
        POST /predict with a valid CustomerInput must return 200 with the
        expected response structure: status, model_version, result containing
        churn_prediction (bool), churn_probability (float in [0,1]), risk_level.
        """
        response = api_client.post("/predict", json=sample_raw_row)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert "status" in body, f"Missing 'status' key: {body}"
        assert "model_version" in body, f"Missing 'model_version' key: {body}"
        assert "result" in body, f"Missing 'result' key: {body}"

        result = body["result"]
        assert isinstance(result["churn_prediction"], bool), (
            f"churn_prediction must be bool: {result['churn_prediction']}"
        )
        assert isinstance(result["churn_probability"], float), (
            f"churn_probability must be float: {result['churn_probability']}"
        )
        assert 0.0 <= result["churn_probability"] <= 1.0, (
            f"churn_probability out of [0,1]: {result['churn_probability']}"
        )
        assert result["risk_level"] in ("high", "medium", "low"), (
            f"risk_level must be one of high/medium/low: {result['risk_level']}"
        )

    def test_predict_shap_values_present_and_dict(self, api_client, sample_raw_row):
        """
        POST /predict must return result.shap_values as a non-null dict where
        every key is a string and every value is a float.
        """
        response = api_client.post("/predict", json=sample_raw_row)

        assert response.status_code == 200
        result = response.json()["result"]
        shap_values = result.get("shap_values")
        assert shap_values is not None, "Expected shap_values to be present (not null)"
        assert isinstance(shap_values, dict), (
            f"shap_values must be a dict, got {type(shap_values)}"
        )
        for k, v in shap_values.items():
            assert isinstance(k, str), f"shap_values key must be str: {k!r}"
            assert isinstance(v, float), f"shap_values value must be float: {v!r}"

    def test_predict_returns_422_for_invalid_tenure(self, api_client, sample_raw_row):
        """
        POST /predict with tenure=999 (outside valid range 1–72) must return 422.
        Response body must reference the 'tenure' field.
        """
        payload = dict(sample_raw_row)
        payload["tenure"] = 999

        response = api_client.post("/predict", json=payload)

        assert response.status_code == 422, (
            f"Expected 422 for invalid tenure, got {response.status_code}: {response.text}"
        )
        assert "tenure" in response.text.lower(), (
            f"Expected 'tenure' mentioned in 422 response: {response.text}"
        )

    def test_predict_returns_422_for_invalid_contract_value(
        self, api_client, sample_raw_row
    ):
        """
        POST /predict with Contract='Weekly' (not an allowed enum value) must
        return 422.
        """
        payload = dict(sample_raw_row)
        payload["Contract"] = "Weekly"

        response = api_client.post("/predict", json=payload)

        assert response.status_code == 422, (
            f"Expected 422 for invalid Contract, got {response.status_code}: {response.text}"
        )

    def test_predict_returns_422_for_missing_required_field(
        self, api_client, sample_raw_row
    ):
        """
        POST /predict with MonthlyCharges omitted must return 422.
        """
        payload = {k: v for k, v in sample_raw_row.items() if k != "MonthlyCharges"}

        response = api_client.post("/predict", json=payload)

        assert response.status_code == 422, (
            f"Expected 422 for missing MonthlyCharges, got {response.status_code}: {response.text}"
        )


# ---------------------------------------------------------------------------
# Task 5.2.2 — TestPredictWhenModelNotReady
# ---------------------------------------------------------------------------

class TestPredictWhenModelNotReady:
    """Tests for POST /predict when the model is not ready (degraded mode)."""

    def test_predict_returns_503_when_model_not_loaded(
        self, degraded_api_client, sample_raw_row
    ):
        """
        POST /predict must return 503 when predictor._is_ready is False.
        The response body must contain a message explaining the model is not ready.
        """
        response = degraded_api_client.post("/predict", json=sample_raw_row)

        assert response.status_code == 503, (
            f"Expected 503 when model not ready, got {response.status_code}: {response.text}"
        )
        body = response.json()
        # The API returns {"status": "error", "message": "..."} for 503 responses
        message = body.get("message", "") or body.get("detail", "")
        assert message, f"Expected non-empty message in 503 response: {body}"


# ---------------------------------------------------------------------------
# Task 5.3.1 — TestBatchPredictEndpoint
# ---------------------------------------------------------------------------

class TestBatchPredictEndpoint:
    """Tests for POST /predict/batch endpoint."""

    def test_batch_predict_returns_correct_count(self, api_client, sample_raw_row):
        """
        POST /predict/batch with 5 valid inputs must return 200, total_input=5,
        5 result items with index 0–4, and shap_values=null for all items.
        The endpoint takes a bare JSON array (List[CustomerInput]), not a wrapped object.
        """
        response = api_client.post("/predict/batch", json=[sample_raw_row] * 5)

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert body["total_input"] == 5, (
            f"Expected total_input=5: {body['total_input']}"
        )
        results = body["results"]
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        for i, item in enumerate(results):
            assert item["index"] == i, (
                f"Expected index={i}, got {item['index']}"
            )
            assert item.get("shap_values") is None, (
                f"Expected shap_values=null in batch, got {item.get('shap_values')}"
            )

    def test_batch_predict_returns_422_for_empty_list(self, api_client):
        """
        POST /predict/batch with an empty list must return 422.
        The endpoint takes a bare JSON array.
        """
        response = api_client.post("/predict/batch", json=[])

        assert response.status_code == 422, (
            f"Expected 422 for empty batch, got {response.status_code}: {response.text}"
        )

    def test_batch_predict_returns_422_when_exceeding_limit(
        self, api_client, sample_raw_row
    ):
        """
        POST /predict/batch with 1001 inputs (over the 1000 limit) must return 422.
        The endpoint takes a bare JSON array.
        """
        response = api_client.post("/predict/batch", json=[sample_raw_row] * 1001)

        assert response.status_code == 422, (
            f"Expected 422 for 1001-item batch, got {response.status_code}: {response.text}"
        )


# ---------------------------------------------------------------------------
# Task 5.3.2 — TestBatchCsvEndpoint
# ---------------------------------------------------------------------------

class TestBatchCsvEndpoint:
    """Tests for POST /predict/batch-csv endpoint."""

    def test_batch_csv_returns_200_with_valid_csv(
        self, api_client, sample_raw_df
    ):
        """
        POST /predict/batch-csv with a valid CSV must return 200.
        total_input must match the number of data rows in the CSV.
        """
        # Drop target and id columns if present — endpoint only needs input features
        csv_df = sample_raw_df.drop(
            columns=["Churn", "id"], errors="ignore"
        )
        csv_string = csv_df.to_csv(index=False)
        expected_rows = len(csv_df)

        response = api_client.post(
            "/predict/batch-csv",
            files={"file": ("test.csv", csv_string.encode(), "text/csv")},
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert body["total_input"] == expected_rows, (
            f"Expected total_input={expected_rows}, got {body['total_input']}"
        )

    def test_batch_csv_returns_422_for_non_csv_file(self, api_client):
        """
        POST /predict/batch-csv with a .json file must return 422.
        """
        response = api_client.post(
            "/predict/batch-csv",
            files={"file": ("test.json", b'{"key": "value"}', "application/json")},
        )

        assert response.status_code == 422, (
            f"Expected 422 for non-CSV file, got {response.status_code}: {response.text}"
        )

    def test_batch_csv_returns_422_when_required_column_missing(self, api_client):
        """
        POST /predict/batch-csv with a CSV missing the 'Contract' column must
        return 422. The response must mention the missing column name.
        """
        csv_string = (
            "tenure,MonthlyCharges,TotalCharges\n"
            "3,85.5,256.5\n"
        )

        response = api_client.post(
            "/predict/batch-csv",
            files={"file": ("test.csv", csv_string.encode(), "text/csv")},
        )

        assert response.status_code == 422, (
            f"Expected 422 for CSV missing Contract, got {response.status_code}: {response.text}"
        )

    def test_batch_csv_drops_id_and_churn_columns_if_present(
        self, api_client, sample_raw_df
    ):
        """
        POST /predict/batch-csv with a CSV that includes 'id' and 'Churn' columns
        must not return an error — the endpoint must silently drop them.
        """
        csv_string = sample_raw_df.to_csv(index=False)  # includes id and Churn

        response = api_client.post(
            "/predict/batch-csv",
            files={"file": ("test.csv", csv_string.encode(), "text/csv")},
        )

        assert response.status_code == 200, (
            f"Expected 200 when CSV contains id/Churn (should be dropped), "
            f"got {response.status_code}: {response.text}"
        )
