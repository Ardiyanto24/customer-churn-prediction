# src/evaluation/metrics.py
#
# Fungsi kalkulasi metric untuk evaluasi model klasifikasi biner (churn prediction).
# Digunakan oleh pipeline training dan oleh test suite DEV-04.

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.utils.logger import get_logger

logger = get_logger("src.evaluation.metrics")


def compute_metrics(y_true, y_prob, threshold: float = 0.5) -> dict:
    """
    Compute standard binary classification metrics for churn prediction.

    Parameters
    ----------
    y_true : array-like of int
        Ground truth binary labels (0 = no churn, 1 = churn).
    y_prob : array-like of float
        Predicted probabilities for the positive class (churn).
        Accepts hard predictions (0/1) as well — they will be thresholded
        at the given threshold value.
    threshold : float, optional
        Decision threshold for converting probabilities to hard predictions.
        Default 0.5.
        Lower threshold → higher recall, lower precision.
        Higher threshold → lower recall, higher precision.

    Returns
    -------
    dict
        Keys: ``precision``, ``recall``, ``f1``, ``roc_auc``, ``pr_auc``.
        All values are Python floats.
    """
    y_true_arr = np.asarray(y_true, dtype=int)
    y_prob_arr = np.asarray(y_prob, dtype=float)
    y_pred_arr = (y_prob_arr >= threshold).astype(int)

    precision = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    recall = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))
    roc_auc = float(roc_auc_score(y_true_arr, y_prob_arr))
    pr_auc = float(average_precision_score(y_true_arr, y_prob_arr))

    logger.debug(
        "Metrics | threshold=%.2f | precision=%.4f | recall=%.4f | "
        "f1=%.4f | roc_auc=%.4f | pr_auc=%.4f",
        threshold,
        precision,
        recall,
        f1,
        roc_auc,
        pr_auc,
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
    }
