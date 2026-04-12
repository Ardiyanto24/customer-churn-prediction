# src/xai/xai_validator.py
#
# XAI quality gate for churn prediction model deployment.
#
# Verifies that the model's top-N SHAP features align with domain expectations
# before promoting a model to production. A model that misses too many domain-
# important features is likely memorising noise rather than learning real signal.

from typing import Dict, List, Optional

from src.utils.logger import get_logger
from config import settings

logger = get_logger("src.xai.xai_validator")


def validate_xai(
    shap_values: Dict[str, float],
    expected_features: Optional[List[str]] = None,
    top_n: Optional[int] = None,
    min_overlap: Optional[float] = None,
) -> bool:
    """
    XAI quality gate: checks whether domain-important features appear in the
    model's top-N SHAP features.

    Supports OHE prefix matching: if "Contract" is an expected feature, any
    SHAP key starting with "Contract_" (e.g. "Contract_Month-to-month") is
    counted as a match. This handles both raw SHAP dicts (OHE'd keys) and
    aggregated SHAP dicts (original feature names).

    Parameters
    ----------
    shap_values : dict
        ``{feature_name: importance_value}`` — absolute SHAP values or any
        non-negative importance scores.  Keys may be original feature names or
        OHE-expanded names (e.g. ``"Contract_Two year"``).
    expected_features : list of str, optional
        Features expected to rank in the top-N.
        Defaults to ``settings.EXPECTED_IMPORTANT_FEATURES``.
    top_n : int, optional
        Number of top features to consider.
        Defaults to ``settings.XAI_TOP_N_FEATURES``.
    min_overlap : float, optional
        Minimum fraction of expected features that must appear in top-N.
        Range [0.0, 1.0].  Defaults to ``settings.XAI_MIN_OVERLAP``.

    Returns
    -------
    bool
        ``True`` if the fraction of expected features found in top-N is ≥
        ``min_overlap``; ``False`` otherwise.
    """
    expected = expected_features if expected_features is not None else settings.EXPECTED_IMPORTANT_FEATURES
    n = top_n if top_n is not None else settings.XAI_TOP_N_FEATURES
    threshold = min_overlap if min_overlap is not None else settings.XAI_MIN_OVERLAP

    if not shap_values:
        logger.warning("XAI gate received empty shap_values dict — returning False.")
        return False

    if not expected:
        logger.warning("XAI gate: expected_features list is empty — returning False.")
        return False

    # Sort by importance descending and take top-N
    sorted_features = sorted(shap_values.items(), key=lambda x: x[1], reverse=True)
    top_n_names = [feat for feat, _ in sorted_features[:n]]

    # Count matched expected features (with OHE prefix support)
    matched: List[str] = []
    missing: List[str] = []

    for exp_feat in expected:
        found = any(
            top_feat == exp_feat or top_feat.startswith(exp_feat + "_")
            for top_feat in top_n_names
        )
        if found:
            matched.append(exp_feat)
        else:
            missing.append(exp_feat)

    overlap = len(matched) / len(expected)
    passes = overlap >= threshold

    logger.info(
        "XAI gate | top_n=%d | min_overlap=%.2f | matched=%d/%d | overlap=%.2f | passes=%s",
        n,
        threshold,
        len(matched),
        len(expected),
        overlap,
        passes,
    )

    if not passes:
        logger.warning(
            "XAI gate FAILED. Features missing from top-%d: %s",
            n,
            missing,
        )
    else:
        logger.debug("XAI gate PASSED. Matched features: %s", matched)

    return passes
