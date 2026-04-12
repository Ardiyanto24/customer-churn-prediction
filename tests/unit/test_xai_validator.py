# tests/unit/test_xai_validator.py
#
# Unit tests for src/xai/xai_validator.py.
# All tests are isolated — no model artifacts, no file I/O, no network calls.

import logging

import pytest

from config import settings
from src.xai.xai_validator import validate_xai

# Mark every test in this module as a unit test
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Task 4.1.1 — Helper function (module-level, not a fixture)
# ---------------------------------------------------------------------------

def build_mock_shap_values(
    top_features: list,
    other_features: list,
) -> dict:
    """
    Build a synthetic SHAP importance dict for use in XAI validator tests.

    Parameters
    ----------
    top_features : list of str
        Feature names assigned high importance values in [0.5, 1.0].
        Ordered from most to least important within the top group.
    other_features : list of str
        Feature names assigned low importance values in [0.01, 0.1].

    Returns
    -------
    dict
        ``{feature_name: importance_value}``
    """
    result: dict = {}

    n_top = max(len(top_features), 1)
    step_top = 0.5 / n_top  # spread values across [0.5, 1.0]
    for i, feat in enumerate(top_features):
        result[feat] = round(1.0 - i * step_top, 4)

    n_other = max(len(other_features), 1)
    step_other = 0.09 / n_other  # spread values across [0.01, 0.1]
    for i, feat in enumerate(other_features):
        result[feat] = round(0.1 - i * step_other, 4)

    return result


# ---------------------------------------------------------------------------
# Task 4.1.2 — TestXAIValidatorPass
# ---------------------------------------------------------------------------

class TestXAIValidatorPass:
    """Tests for scenarios where the XAI quality gate should return True."""

    def test_model_passes_when_all_expected_features_in_top_n(self):
        """
        When all EXPECTED_IMPORTANT_FEATURES are among the top-XAI_TOP_N_FEATURES
        features, the gate must pass.
        """
        # Put all 5 expected features in positions 1-5, fill the rest with noise
        top_features = settings.EXPECTED_IMPORTANT_FEATURES + [
            "noise_feat_1", "noise_feat_2", "noise_feat_3",
            "noise_feat_4", "noise_feat_5",
        ]
        other_features = ["irrelevant_a", "irrelevant_b"]
        shap_values = build_mock_shap_values(top_features, other_features)

        result = validate_xai(shap_values)

        assert result is True

    def test_model_passes_at_exact_minimum_overlap(self):
        """
        With exactly 3 of 5 expected features in top-10 (overlap = 3/5 = 0.6
        ≥ XAI_MIN_OVERLAP = 0.5), the gate must pass.
        3 is the minimum count that satisfies the 50% threshold for 5 features.
        """
        expected = settings.EXPECTED_IMPORTANT_FEATURES  # e.g. ["Contract", "tenure", ...]

        # 3 expected in top, 2 expected assigned low values
        top_features = expected[:3] + [
            "noise_1", "noise_2", "noise_3", "noise_4", "noise_5", "noise_6", "noise_7"
        ]
        other_features = expected[3:]  # 2 expected features with low importance
        shap_values = build_mock_shap_values(top_features, other_features)

        result = validate_xai(shap_values)

        assert result is True

    def test_validator_returns_bool_not_none(self):
        """
        Return type must be exactly bool — not None, not int, not float.
        This guards against validators that return truthy/falsy non-bool values.
        """
        shap_values = build_mock_shap_values(
            top_features=settings.EXPECTED_IMPORTANT_FEATURES,
            other_features=["other_1", "other_2", "other_3", "other_4", "other_5"],
        )
        result = validate_xai(shap_values)

        assert isinstance(result, bool), (
            f"validate_xai() must return bool, got {type(result).__name__}"
        )

    def test_prefix_matching_handles_ohe_expanded_feature_names(self):
        """
        When SHAP values contain OHE-expanded names (e.g. "Contract_Two year"),
        the validator must match them against the original feature name "Contract".
        This supports cases where raw SHAP dicts are passed before OHE aggregation.
        """
        # Replace "Contract" and "InternetService" with OHE-expanded equivalents
        ohe_top_features = [
            "Contract_Two year",          # matches expected "Contract"
            "InternetService_Fiber optic", # matches expected "InternetService"
            "tenure",
            "MonthlyCharges",
            "tc_residual",
            "noise_1", "noise_2", "noise_3", "noise_4", "noise_5",
        ]
        shap_values = build_mock_shap_values(ohe_top_features, ["irrelevant_x"])

        result = validate_xai(shap_values)

        assert result is True, (
            "Validator should match OHE-expanded names via prefix matching"
        )
