# tests/unit/test_preprocessing.py
#
# Unit tests for src/preprocessing/ components.
# All tests are isolated — no model artifacts, no file I/O, no network calls.

import numpy as np
import pandas as pd
import pytest

from src.preprocessing.encoders import StructuralEncoder, BinaryEncoder, OHEWrapper
from src.preprocessing.feature_engineering import FeatureEngineer, ColumnDropper
from src.preprocessing.pipeline import PreprocessingPipeline
from config import settings

# Mark every test in this module as a unit test
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Task 2.1.1 — TestStructuralEncoder
# ---------------------------------------------------------------------------

class TestStructuralEncoder:
    """
    Tests for StructuralEncoder in src/preprocessing/encoders.py.

    Key invariant: "No internet service" and "No phone service" are structural
    values — they must be encoded differently from plain "No".
    """

    def test_no_internet_service_encoded_differently_from_no(self):
        """
        "No internet service" encodes to -1; plain "No" encodes to 0.
        They must produce distinct numeric values, not both map to 0.
        """
        encoder = StructuralEncoder(cols=["OnlineSecurity"])
        df = pd.DataFrame({"OnlineSecurity": ["No internet service", "No"]})
        encoder.fit(df)
        result = encoder.transform(df)

        encoded_no_internet = result.loc[0, "OnlineSecurity"]
        encoded_no = result.loc[1, "OnlineSecurity"]

        assert encoded_no_internet != encoded_no, (
            f"Expected 'No internet service' ({encoded_no_internet}) "
            f"to differ from 'No' ({encoded_no})"
        )

    def test_no_phone_service_encoded_differently_from_no(self):
        """
        "No phone service" encodes to -1; plain "No" encodes to 0.
        They must produce distinct numeric values.
        """
        encoder = StructuralEncoder(cols=["MultipleLines"])
        df = pd.DataFrame({"MultipleLines": ["No phone service", "No"]})
        encoder.fit(df)
        result = encoder.transform(df)

        encoded_no_phone = result.loc[0, "MultipleLines"]
        encoded_no = result.loc[1, "MultipleLines"]

        assert encoded_no_phone != encoded_no, (
            f"Expected 'No phone service' ({encoded_no_phone}) "
            f"to differ from 'No' ({encoded_no})"
        )

    def test_encoder_only_fit_on_training_data_does_not_crash_on_unseen_values(self):
        """
        Encoder is fit on training data only. At inference time it may encounter
        values not seen during training. It must not crash — unknown values pass
        through unchanged (fillna behaviour in StructuralEncoder.transform).
        """
        train_df = pd.DataFrame(
            {"OnlineSecurity": ["Yes", "No", "No internet service"]}
        )
        test_df = pd.DataFrame({"OnlineSecurity": ["Yes", "UNKNOWN_VALUE"]})

        encoder = StructuralEncoder(cols=["OnlineSecurity"])
        encoder.fit(train_df)
        result = encoder.transform(test_df)

        # Must not crash; output shape must match input shape
        assert result.shape == test_df.shape

        # Unknown value passes through unchanged (fillna keeps original string)
        assert result.loc[1, "OnlineSecurity"] == "UNKNOWN_VALUE"


# ---------------------------------------------------------------------------
# Task 2.1.2 — TestFeatureEngineering
# ---------------------------------------------------------------------------

class TestFeatureEngineering:
    """
    Tests for FeatureEngineer in src/preprocessing/feature_engineering.py.

    Each test uses a minimal DataFrame containing only the columns required
    by the specific feature under test.
    """

    def test_tc_residual_is_difference_from_expected(self):
        """
        tc_residual = TotalCharges − (tenure × MonthlyCharges).
        Example: 300.0 − (3 × 90.0) = 30.0
        """
        fe = FeatureEngineer()
        df = pd.DataFrame({
            "TotalCharges": [300.0],
            "tenure": [3],
            "MonthlyCharges": [90.0],
        })
        result = fe.transform(df)
        expected = 300.0 - (3 * 90.0)  # 30.0
        assert abs(result.loc[0, "tc_residual"] - expected) < 1e-6

    def test_monthly_to_total_ratio_computed_correctly(self):
        """
        monthly_to_total_ratio = MonthlyCharges / TotalCharges.
        Example: 80.0 / 400.0 = 0.2
        """
        fe = FeatureEngineer()
        df = pd.DataFrame({
            "TotalCharges": [400.0],
            "tenure": [5],
            "MonthlyCharges": [80.0],
        })
        result = fe.transform(df)
        expected = 80.0 / 400.0  # 0.2
        assert abs(result.loc[0, "monthly_to_total_ratio"] - expected) < 1e-6

    def test_tenure_group_uses_correct_boundaries(self):
        """
        Boundaries [0, 2, 18, 44, 72] with right=True, include_lowest=True:
          G1_0_2   : tenure ∈ [0, 2]
          G2_2_18  : tenure ∈ (2, 18]
          G3_18_44 : tenure ∈ (18, 44]
          G4_44_72 : tenure ∈ (44, 72]
        """
        fe = FeatureEngineer()
        df = pd.DataFrame({
            "tenure": [1, 10, 30, 60],
            "MonthlyCharges": [50.0, 50.0, 50.0, 50.0],
            "TotalCharges": [50.0, 500.0, 1500.0, 3000.0],
        })
        result = fe.transform(df)

        assert result.loc[0, "tenure_group"] == "G1_0_2",  f"tenure=1 expected G1_0_2, got {result.loc[0, 'tenure_group']}"
        assert result.loc[1, "tenure_group"] == "G2_2_18", f"tenure=10 expected G2_2_18, got {result.loc[1, 'tenure_group']}"
        assert result.loc[2, "tenure_group"] == "G3_18_44", f"tenure=30 expected G3_18_44, got {result.loc[2, 'tenure_group']}"
        assert result.loc[3, "tenure_group"] == "G4_44_72", f"tenure=60 expected G4_44_72, got {result.loc[3, 'tenure_group']}"

    def test_service_count_counts_only_active_addons(self):
        """
        service_count counts only add-ons with value "Yes".
        "No" and "No internet service" must not be counted.
        """
        fe = FeatureEngineer()
        df = pd.DataFrame({
            "TotalCharges": [500.0],
            "tenure": [10],
            "MonthlyCharges": [50.0],
            # 3 active ("Yes"), 2 inactive ("No"), 1 structural ("No internet service")
            "OnlineSecurity": ["Yes"],
            "OnlineBackup": ["Yes"],
            "DeviceProtection": ["Yes"],
            "TechSupport": ["No"],
            "StreamingTV": ["No"],
            "StreamingMovies": ["No internet service"],
        })
        result = fe.transform(df)
        assert result.loc[0, "service_count"] == 3

    def test_is_auto_payment_true_for_automatic_methods(self):
        """
        is_auto_payment = 1 for "Bank transfer (automatic)" and
        "Credit card (automatic)"; = 0 for manual payment methods.
        """
        fe = FeatureEngineer()
        df = pd.DataFrame({
            "PaymentMethod": [
                "Bank transfer (automatic)",
                "Credit card (automatic)",
                "Electronic check",
                "Mailed check",
            ]
        })
        result = fe.transform(df)

        assert result.loc[0, "is_auto_payment"] == 1, "Bank transfer (automatic) should be is_auto_payment=1"
        assert result.loc[1, "is_auto_payment"] == 1, "Credit card (automatic) should be is_auto_payment=1"
        assert result.loc[2, "is_auto_payment"] == 0, "Electronic check should be is_auto_payment=0"
        assert result.loc[3, "is_auto_payment"] == 0, "Mailed check should be is_auto_payment=0"


# ---------------------------------------------------------------------------
# Task 2.2.1 — TestPipelineSerialization
# ---------------------------------------------------------------------------

class TestPipelineSerialization:
    """
    Tests for training-serving parity of PreprocessingPipeline.

    Verifies that:
    - Serialization via joblib does not change numeric outputs (roundtrip parity)
    - Pipeline output contains no NaN values in numeric columns
    - Number of output columns is stable regardless of input row count
    """

    def test_pipeline_output_consistent_after_joblib_roundtrip(
        self, dummy_preprocessor, sample_raw_df, tmp_path
    ):
        """
        Serializing a fitted pipeline with joblib.dump and reloading with
        joblib.load must produce bit-for-bit identical numeric outputs.
        Any divergence would indicate state loss during serialization.
        """
        import joblib

        X = sample_raw_df.drop(
            columns=[settings.TARGET_COLUMN, settings.ID_COLUMN], errors="ignore"
        )
        output_before = dummy_preprocessor.transform(X)

        pipeline_path = tmp_path / "test_roundtrip_pipeline.joblib"
        joblib.dump(dummy_preprocessor, pipeline_path)
        loaded_pipeline = joblib.load(pipeline_path)
        output_after = loaded_pipeline.transform(X)

        # Compare numeric columns only (string pass-throughs are not floats)
        numeric_cols = output_before.select_dtypes(include=[np.number]).columns
        np.testing.assert_array_almost_equal(
            output_before[numeric_cols].values,
            output_after[numeric_cols].values,
            decimal=6,
            err_msg="Joblib roundtrip changed numeric pipeline outputs",
        )

    def test_pipeline_transform_produces_no_nan(
        self, dummy_preprocessor, sample_raw_df
    ):
        """
        No NaN values should appear in any numeric column after transform.
        NaN in numeric outputs would silently corrupt model predictions.
        """
        X = sample_raw_df.drop(
            columns=[settings.TARGET_COLUMN, settings.ID_COLUMN], errors="ignore"
        )
        output = dummy_preprocessor.transform(X)

        numeric_cols = output.select_dtypes(include=[np.number]).columns
        assert not np.isnan(output[numeric_cols].values).any(), (
            "Pipeline transform produced NaN values in numeric columns"
        )

    def test_pipeline_fit_and_transform_produce_same_shape(
        self, sample_raw_df
    ):
        """
        A freshly fitted pipeline must produce the same number of columns
        regardless of how many rows are passed to transform.
        Column count consistency is required for serving parity.
        """
        X = sample_raw_df.drop(
            columns=[settings.TARGET_COLUMN, settings.ID_COLUMN], errors="ignore"
        )
        pipeline = PreprocessingPipeline()
        output_full = pipeline.fit_transform(X)

        # Transform a different-sized slice — column count must be identical
        X_small = X.iloc[:5].reset_index(drop=True)
        output_small = pipeline.transform(X_small)

        assert output_full.shape[1] == output_small.shape[1], (
            f"Column count changed: fit_transform={output_full.shape[1]}, "
            f"transform (5 rows)={output_small.shape[1]}"
        )
