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
