# tests/conftest.py
#
# Shared fixtures untuk seluruh test suite DEV-04.
# Tersedia otomatis untuk semua test di tests/ tanpa perlu di-import manual.
#
# Scope strategy:
#   - sample_raw_row  : function  — fresh dict per test
#   - sample_raw_df   : function  — fresh DataFrame per test
#   - dummy_preprocessor : session — fit sekali, reused oleh semua test
#   - dummy_model     : session  — trained sekali, reused oleh semua test
#   - api_client      : function  — TestClient baru per test, state predictor di-reset

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from starlette.testclient import TestClient

from config import settings
from src.preprocessing.pipeline import PreprocessingPipeline


# ---------------------------------------------------------------------------
# Internal helper — builds the 20-row raw DataFrame.
# Defined as a plain function (not a fixture) so that both function-scoped
# and session-scoped fixtures can call it without scope-mismatch errors.
# ---------------------------------------------------------------------------

def _build_sample_df() -> pd.DataFrame:
    """
    Build a 20-row synthetic DataFrame matching the full raw data schema.

    Variation coverage:
      - InternetService = "No"  → add-on columns carry "No internet service"
      - PhoneService = "No"     → MultipleLines carries "No phone service"
      - Contract: all three variants (Month-to-month, One year, Two year)
      - tenure: ranges from 1 to 72
      - Churn distribution: 5 "Yes", 15 "No"  (realistic class imbalance)
    """
    rows = [
        # ── High-churn risk (5 rows, Churn = "Yes") ─────────────────────────
        {
            "id": "H001", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 2,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "No",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 85.50, "TotalCharges": 171.00, "Churn": "Yes",
        },
        {
            "id": "H002", "gender": "Female", "SeniorCitizen": 1,
            "Partner": "No", "Dependents": "No", "tenure": 3,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No", "OnlineBackup": "No",
            "DeviceProtection": "Yes", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "Yes",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 99.65, "TotalCharges": 298.95, "Churn": "Yes",
        },
        {
            "id": "H003", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 1,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 70.70, "TotalCharges": 70.70, "Churn": "Yes",
        },
        {
            "id": "H004", "gender": "Female", "SeniorCitizen": 1,
            "Partner": "No", "Dependents": "No", "tenure": 5,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No", "OnlineBackup": "Yes",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "No", "StreamingMovies": "Yes",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 89.10, "TotalCharges": 445.50, "Churn": "Yes",
        },
        {
            "id": "H005", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 4,
            "PhoneService": "No", "MultipleLines": "No phone service",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "Yes",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 75.40, "TotalCharges": 301.60, "Churn": "Yes",
        },
        # ── Low-churn risk (10 rows, Churn = "No") ──────────────────────────
        {
            "id": "L001", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "Yes", "tenure": 60,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "Yes",
            "DeviceProtection": "Yes", "TechSupport": "Yes",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Two year", "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 65.00, "TotalCharges": 3900.00, "Churn": "No",
        },
        {
            "id": "L002", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "No", "tenure": 48,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "No",
            "DeviceProtection": "Yes", "TechSupport": "Yes",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Two year", "PaperlessBilling": "No",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 59.90, "TotalCharges": 2875.20, "Churn": "No",
        },
        {
            "id": "L003", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "Yes", "tenure": 72,
            "PhoneService": "No", "MultipleLines": "No phone service",
            "InternetService": "No",
            "OnlineSecurity": "No internet service",
            "OnlineBackup": "No internet service",
            "DeviceProtection": "No internet service",
            "TechSupport": "No internet service",
            "StreamingTV": "No internet service",
            "StreamingMovies": "No internet service",
            "Contract": "Two year", "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 20.15, "TotalCharges": 1450.80, "Churn": "No",
        },
        {
            "id": "L004", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "Yes", "tenure": 55,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "Yes",
            "DeviceProtection": "Yes", "TechSupport": "Yes",
            "StreamingTV": "Yes", "StreamingMovies": "Yes",
            "Contract": "One year", "PaperlessBilling": "No",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 80.50, "TotalCharges": 4427.50, "Churn": "No",
        },
        {
            "id": "L005", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 30,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "One year", "PaperlessBilling": "Yes",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 45.00, "TotalCharges": 1350.00, "Churn": "No",
        },
        {
            "id": "L006", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "Yes", "tenure": 65,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "Yes",
            "DeviceProtection": "No", "TechSupport": "Yes",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Two year", "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 62.75, "TotalCharges": 4078.75, "Churn": "No",
        },
        {
            "id": "L007", "gender": "Female", "SeniorCitizen": 1,
            "Partner": "Yes", "Dependents": "No", "tenure": 40,
            "PhoneService": "No", "MultipleLines": "No phone service",
            "InternetService": "No",
            "OnlineSecurity": "No internet service",
            "OnlineBackup": "No internet service",
            "DeviceProtection": "No internet service",
            "TechSupport": "No internet service",
            "StreamingTV": "No internet service",
            "StreamingMovies": "No internet service",
            "Contract": "One year", "PaperlessBilling": "No",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 19.90, "TotalCharges": 796.00, "Churn": "No",
        },
        {
            "id": "L008", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "Yes", "tenure": 50,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "Yes",
            "DeviceProtection": "Yes", "TechSupport": "No",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Two year", "PaperlessBilling": "No",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 55.25, "TotalCharges": 2762.50, "Churn": "No",
        },
        {
            "id": "L009", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 22,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "DSL",
            "OnlineSecurity": "No", "OnlineBackup": "Yes",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "One year", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 51.30, "TotalCharges": 1128.60, "Churn": "No",
        },
        {
            "id": "L010", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "Yes", "tenure": 35,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes", "OnlineBackup": "No",
            "DeviceProtection": "Yes", "TechSupport": "Yes",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "One year", "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 60.40, "TotalCharges": 2114.00, "Churn": "No",
        },
        # ── Mixed profiles (5 rows, Churn = "No") ───────────────────────────
        {
            "id": "M001", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 12,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "Yes", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "Yes",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Credit card (automatic)",
            "MonthlyCharges": 74.35, "TotalCharges": 892.20, "Churn": "No",
        },
        {
            "id": "M002", "gender": "Male", "SeniorCitizen": 1,
            "Partner": "Yes", "Dependents": "No", "tenure": 18,
            "PhoneService": "Yes", "MultipleLines": "Yes",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "Yes", "OnlineBackup": "Yes",
            "DeviceProtection": "Yes", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "No",
            "Contract": "Month-to-month", "PaperlessBilling": "No",
            "PaymentMethod": "Mailed check",
            "MonthlyCharges": 95.00, "TotalCharges": 1710.00, "Churn": "No",
        },
        {
            "id": "M003", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "No", "Dependents": "No", "tenure": 8,
            "PhoneService": "No", "MultipleLines": "No phone service",
            "InternetService": "DSL",
            "OnlineSecurity": "No", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "Yes",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 49.90, "TotalCharges": 399.20, "Churn": "No",
        },
        {
            "id": "M004", "gender": "Male", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "No", "tenure": 25,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "No",
            "OnlineSecurity": "No internet service",
            "OnlineBackup": "No internet service",
            "DeviceProtection": "No internet service",
            "TechSupport": "No internet service",
            "StreamingTV": "No internet service",
            "StreamingMovies": "No internet service",
            "Contract": "One year", "PaperlessBilling": "No",
            "PaymentMethod": "Bank transfer (automatic)",
            "MonthlyCharges": 25.35, "TotalCharges": 633.75, "Churn": "No",
        },
        {
            "id": "M005", "gender": "Female", "SeniorCitizen": 1,
            "Partner": "No", "Dependents": "No", "tenure": 15,
            "PhoneService": "Yes", "MultipleLines": "No",
            "InternetService": "Fiber optic",
            "OnlineSecurity": "No", "OnlineBackup": "No",
            "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "No", "StreamingMovies": "No",
            "Contract": "Month-to-month", "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 69.65, "TotalCharges": 1044.75, "Churn": "No",
        },
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Task 1.2.1 — sample_raw_row fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def sample_raw_row() -> dict:
    """
    Single raw customer row matching the full raw data schema.
    Represents a high-churn-risk profile:
      - Month-to-month contract, short tenure, Fiber optic, no security add-ons,
        electronic check payment — all strong churn signals.
    """
    return {
        "id": "TEST001",
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 3,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "No",
        "StreamingMovies": "No",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 85.5,
        "TotalCharges": 256.5,
    }


# ---------------------------------------------------------------------------
# Task 1.2.2 — sample_raw_df fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def sample_raw_df() -> pd.DataFrame:
    """
    20-row synthetic DataFrame with realistic variation across all raw columns.
    Includes the Churn label (5 Yes / 15 No) for use in preprocessing unit tests.
    Built programmatically — no file I/O.
    """
    return _build_sample_df()


# ---------------------------------------------------------------------------
# Task 1.2.3 — dummy_preprocessor fixture (session scope)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def dummy_preprocessor() -> PreprocessingPipeline:
    """
    A PreprocessingPipeline that has been fit on the synthetic 20-row dataset.
    Session-scoped: built once and reused across all tests that need it.
    Uses _build_sample_df() directly to avoid scope-mismatch with the
    function-scoped sample_raw_df fixture.

    Raises on import or fit errors — this is expected behaviour indicating
    that src/preprocessing/pipeline.py is not yet implemented.
    """
    df = _build_sample_df()
    X = df.drop(
        columns=[settings.TARGET_COLUMN, settings.ID_COLUMN], errors="ignore"
    )
    pipeline = PreprocessingPipeline()
    pipeline.fit(X)
    return pipeline


# ---------------------------------------------------------------------------
# Task 1.2.4 — dummy_model fixture (session scope)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def dummy_model(dummy_preprocessor: PreprocessingPipeline) -> LogisticRegression:
    """
    A LogisticRegression trained on preprocessed synthetic data.
    Session-scoped: trained once and reused.

    Depends on dummy_preprocessor to ensure feature dimensions match
    exactly what the API will receive at inference time.
    """
    df = _build_sample_df()
    X_raw = df.drop(
        columns=[settings.TARGET_COLUMN, settings.ID_COLUMN], errors="ignore"
    )
    y = (df[settings.TARGET_COLUMN] == settings.CHURN_POSITIVE_LABEL).astype(int)

    X_transformed = dummy_preprocessor.transform(X_raw)
    model = LogisticRegression(
        random_state=settings.RANDOM_SEED, max_iter=1000
    )
    model.fit(X_transformed, y)
    return model


# ---------------------------------------------------------------------------
# Task 1.2.5 — api_client fixture (function scope)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def api_client(dummy_model: LogisticRegression, dummy_preprocessor: PreprocessingPipeline):
    """
    FastAPI TestClient with dummy model and preprocessor injected into the
    predictor singleton. No real joblib artifacts or running server needed.

    Setup:
      1. Start the TestClient (lifespan runs; real artifact load will fail gracefully).
      2. Override predictor state with dummy artifacts.

    Teardown:
      Reset predictor to default state so tests are fully isolated.
    """
    from api.main import app
    from api.predictor import predictor

    with TestClient(app) as client:
        # Lifespan has run — inject dummy artifacts into the singleton
        predictor._model = dummy_model
        predictor._preprocessor = dummy_preprocessor
        predictor._is_ready = True
        predictor._model_version = "dummy_v1"

        yield client

    # Reset to default state after each test
    predictor._model = None
    predictor._preprocessor = None
    predictor._is_ready = False
    predictor._model_version = "unknown"
