# tests/unit/test_metrics.py
#
# Unit tests for src/evaluation/metrics.py.
# All tests use y_true / y_prob values whose expected metric outputs are
# known exactly or bounded analytically — no ML models needed.

import numpy as np
import pytest

from config import settings
from src.evaluation.metrics import compute_metrics

# Mark every test in this module as a unit test
pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Task 3.1.1 — TestMetricCalculations
# ---------------------------------------------------------------------------

class TestMetricCalculations:
    """
    Tests for compute_metrics() covering standard metric correctness.
    Each test uses deterministic y_true / y_prob pairs with analytically
    known expected values.
    """

    def test_perfect_prediction_yields_all_ones(self):
        """
        When predicted scores perfectly separate positives from negatives,
        precision, recall, F1, and ROC-AUC must all equal 1.0.
        """
        y_true = [1, 1, 0, 0, 1]
        y_pred = [1, 1, 0, 0, 1]  # hard predictions == y_true

        result = compute_metrics(y_true, y_pred)

        assert result["precision"] == 1.0, f"Expected precision=1.0, got {result['precision']}"
        assert result["recall"] == 1.0, f"Expected recall=1.0, got {result['recall']}"
        assert result["f1"] == 1.0, f"Expected f1=1.0, got {result['f1']}"
        assert result["roc_auc"] == 1.0, f"Expected roc_auc=1.0, got {result['roc_auc']}"

    def test_all_wrong_prediction_yields_zero_metrics(self):
        """
        When every positive is predicted as negative and vice versa,
        precision and recall must both be 0.0.
        """
        y_true = [1, 1, 0, 0]
        y_pred = [0, 0, 1, 1]  # all inverted

        result = compute_metrics(y_true, y_pred)

        assert result["precision"] == 0.0, (
            f"Expected precision=0.0, got {result['precision']}"
        )
        assert result["recall"] == 0.0, (
            f"Expected recall=0.0, got {result['recall']}"
        )

    def test_roc_auc_random_prediction_near_0_5(self):
        """
        Uncorrelated probabilities (pure random) should yield ROC-AUC close
        to 0.5. We allow a wide range [0.3, 0.7] to avoid flaky tests while
        still catching degenerate implementations.
        """
        rng = np.random.default_rng(settings.RANDOM_SEED)
        y_true = rng.integers(0, 2, size=100).tolist()
        y_prob = rng.random(size=100).tolist()

        result = compute_metrics(y_true, y_prob)

        assert 0.3 <= result["roc_auc"] <= 0.7, (
            f"Random ROC-AUC expected in [0.3, 0.7], got {result['roc_auc']:.4f}"
        )

    def test_metric_function_returns_dict_with_required_keys(self):
        """
        compute_metrics() must return a dict containing at minimum the five
        keys that the XAI gate and CI pipeline depend on.
        """
        y_true = [1, 0, 1, 0, 1]
        y_prob = [0.9, 0.1, 0.8, 0.2, 0.7]

        result = compute_metrics(y_true, y_prob)

        assert isinstance(result, dict), "compute_metrics() must return a dict"
        required_keys = {"precision", "recall", "f1", "roc_auc", "pr_auc"}
        missing = required_keys - result.keys()
        assert not missing, f"Missing required keys: {missing}"


# ---------------------------------------------------------------------------
# Task 3.1.2 — PR-AUC and threshold sensitivity tests
# ---------------------------------------------------------------------------

class TestPRAUCAndThreshold:
    """
    PR-AUC is the primary metric for this imbalanced churn problem.
    These tests verify its behaviour under different model quality levels
    and that the threshold parameter correctly governs the tradeoff.
    """

    def test_pr_auc_reflects_class_distribution(self):
        """
        A perfectly discriminating model must yield higher PR-AUC than a
        model using random uncorrelated probabilities.
        """
        # Scenario A: perfect discrimination
        n = 100
        y_true = [1] * (n // 2) + [0] * (n // 2)
        y_prob_perfect = [0.95] * (n // 2) + [0.05] * (n // 2)

        # Scenario B: random uncorrelated probabilities (fixed seed for reproducibility)
        rng = np.random.default_rng(settings.RANDOM_SEED)
        y_prob_random = rng.random(size=n).tolist()

        result_perfect = compute_metrics(y_true, y_prob_perfect)
        result_random = compute_metrics(y_true, y_prob_random)

        assert result_perfect["pr_auc"] > result_random["pr_auc"], (
            f"Perfect PR-AUC ({result_perfect['pr_auc']:.4f}) should exceed "
            f"random PR-AUC ({result_random['pr_auc']:.4f})"
        )

    def test_classification_threshold_affects_precision_recall_tradeoff(self):
        """
        Using a lower threshold predicts more positives → higher recall, lower
        precision. Using a higher threshold predicts fewer positives → lower
        recall, higher precision.
        """
        y_true = [1, 1, 1, 0, 0, 0, 1, 0]
        y_prob = [0.80, 0.70, 0.55, 0.45, 0.35, 0.20, 0.65, 0.40]

        result_low = compute_metrics(y_true, y_prob, threshold=0.3)
        result_high = compute_metrics(y_true, y_prob, threshold=0.7)

        assert result_low["recall"] >= result_high["recall"], (
            f"Lower threshold should yield higher or equal recall: "
            f"low={result_low['recall']:.4f}, high={result_high['recall']:.4f}"
        )
        assert result_low["precision"] <= result_high["precision"], (
            f"Lower threshold should yield lower or equal precision: "
            f"low={result_low['precision']:.4f}, high={result_high['precision']:.4f}"
        )
