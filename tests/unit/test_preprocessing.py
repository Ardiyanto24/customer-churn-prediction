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
