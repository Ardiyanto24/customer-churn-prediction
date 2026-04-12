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


# ---------------------------------------------------------------------------
# Task 4.1.3 — TestXAIValidatorFail
# ---------------------------------------------------------------------------

class TestXAIValidatorFail:
    """Tests for scenarios where the XAI quality gate should return False."""

    def test_model_fails_when_no_expected_features_in_top_n(self):
        """
        When none of the EXPECTED_IMPORTANT_FEATURES appear in the top-N,
        the gate must fail. This catches a model that learned irrelevant signals.
        """
        # All 10 top slots filled with non-domain features
        non_domain_features = [f"noise_feat_{i}" for i in range(1, 11)]
        # Expected features get low importance
        shap_values = build_mock_shap_values(
            top_features=non_domain_features,
            other_features=settings.EXPECTED_IMPORTANT_FEATURES,
        )

        result = validate_xai(shap_values)

        assert result is False

    def test_model_fails_below_minimum_overlap(self):
        """
        With only 2 of 5 expected features in top-10 (overlap = 2/5 = 0.4 <
        XAI_MIN_OVERLAP = 0.5), the gate must fail.
        """
        expected = settings.EXPECTED_IMPORTANT_FEATURES  # 5 features

        # 2 expected in top, 3 expected with low importance
        top_features = expected[:2] + [
            "noise_1", "noise_2", "noise_3",
            "noise_4", "noise_5", "noise_6", "noise_7", "noise_8",
        ]
        other_features = expected[2:]  # 3 expected features with low importance
        shap_values = build_mock_shap_values(top_features, other_features)

        result = validate_xai(shap_values)

        assert result is False

    def test_validator_logs_missing_features_when_gate_fails(self, caplog):
        """
        When the gate fails, the validator must emit a WARNING-level log that
        identifies which expected features were absent from the top-N.
        This allows pipeline operators to diagnose model quality issues.
        """
        # None of the expected features in top-10
        non_domain_features = [f"noise_{i}" for i in range(1, 11)]
        shap_values = build_mock_shap_values(
            top_features=non_domain_features,
            other_features=settings.EXPECTED_IMPORTANT_FEATURES,
        )

        with caplog.at_level(logging.WARNING, logger="src.xai.xai_validator"):
            result = validate_xai(shap_values)

        assert result is False
        warning_messages = [r.message for r in caplog.records if r.levelno >= logging.WARNING]
        assert any("XAI gate FAILED" in msg for msg in warning_messages), (
            f"Expected 'XAI gate FAILED' in warning logs. Got: {warning_messages}"
        )


# ---------------------------------------------------------------------------
# Task 4.1.4 — TestXAIValidatorEdgeCases
# ---------------------------------------------------------------------------

class TestXAIValidatorEdgeCases:
    """
    Tests for custom top_n / min_overlap parameters and their interaction.
    Verifies that the validator uses constants from config/settings.py as
    defaults and accepts overrides without modifying global state.
    """

    def test_validator_with_custom_top_n(self):
        """
        With all 5 expected features at positions 1-5 (and noise at 6-10):
        - top_n=5  → all 5 expected in top-5 → overlap=1.0 → passes (True)
        - top_n=3 + min_overlap=1.0 → only 3/5 in top-3 → overlap=0.6 < 1.0 → fails (False)
        """
        expected = settings.EXPECTED_IMPORTANT_FEATURES  # 5 features

        # Positions 1-5: all 5 expected; positions 6-10: noise
        top_features = list(expected) + [
            "noise_6", "noise_7", "noise_8", "noise_9", "noise_10"
        ]
        shap_values = build_mock_shap_values(top_features, other_features=[])

        # With top_n=5: all 5 expected are in the top-5 → passes
        result_top5 = validate_xai(shap_values, top_n=5)
        assert result_top5 is True, (
            f"top_n=5 with all expected features should pass, got {result_top5}"
        )

        # With top_n=3 and min_overlap=1.0: only 3 of 5 expected in top-3 → fails
        result_top3 = validate_xai(shap_values, top_n=3, min_overlap=1.0)
        assert result_top3 is False, (
            f"top_n=3, min_overlap=1.0 with only 3/5 expected should fail, got {result_top3}"
        )

    def test_validator_with_custom_min_overlap(self):
        """
        With 4 of 5 expected features in top-10 (overlap = 4/5 = 0.8):
        - min_overlap=1.0 → 0.8 < 1.0 → fails (False)
        - min_overlap=0.5 → 0.8 ≥ 0.5 → passes (True)
        """
        expected = settings.EXPECTED_IMPORTANT_FEATURES  # 5 features

        # 4 expected in top-10, 1 expected gets low importance
        top_features = list(expected[:4]) + [
            "noise_1", "noise_2", "noise_3", "noise_4", "noise_5", "noise_6"
        ]
        other_features = list(expected[4:])  # 1 expected feature with low importance
        shap_values = build_mock_shap_values(top_features, other_features)

        # With min_overlap=1.0: 4/5=0.8 < 1.0 → fails
        result_strict = validate_xai(shap_values, min_overlap=1.0)
        assert result_strict is False, (
            f"min_overlap=1.0 with 4/5 matched should fail, got {result_strict}"
        )

        # With min_overlap=0.5: 4/5=0.8 ≥ 0.5 → passes
        result_lenient = validate_xai(shap_values, min_overlap=0.5)
        assert result_lenient is True, (
            f"min_overlap=0.5 with 4/5 matched should pass, got {result_lenient}"
        )

    def test_validator_uses_constants_from_settings(self):
        """
        Default behaviour must be driven by settings.py constants, not hardcoded
        values. Verify that the defaults align with the declared constants.
        """
        expected = settings.EXPECTED_IMPORTANT_FEATURES
        top_n = settings.XAI_TOP_N_FEATURES
        min_overlap = settings.XAI_MIN_OVERLAP

        # Build SHAP values that barely pass with the defaults
        n_expected = len(expected)
        # min required matches = smallest integer ≥ n_expected * min_overlap
        import math
        min_matches = math.ceil(n_expected * min_overlap)

        top_features = list(expected[:min_matches]) + [
            f"noise_{i}" for i in range(top_n - min_matches + 1)
        ]
        other_features = list(expected[min_matches:])
        shap_values = build_mock_shap_values(top_features, other_features)

        result_default = validate_xai(shap_values)
        expected_overlap = min_matches / n_expected
        expected_pass = expected_overlap >= min_overlap

        assert result_default is expected_pass, (
            f"Default validate_xai() should return {expected_pass} "
            f"(overlap={expected_overlap:.2f}, min_overlap={min_overlap}), "
            f"but got {result_default}. "
            f"Check that EXPECTED_IMPORTANT_FEATURES, XAI_TOP_N_FEATURES, "
            f"and XAI_MIN_OVERLAP are imported from config/settings.py."
        )
