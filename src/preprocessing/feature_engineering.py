# src/preprocessing/feature_engineering.py

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

TENURE_BINS = [0, 2, 18, 44, 72]
TENURE_LABELS = ["G1_0_2", "G2_2_18", "G3_18_44", "G4_44_72"]
ADDON_COLS = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]
AUTO_PAYMENT_METHODS = ["Bank transfer (automatic)", "Credit card (automatic)"]
DROP_COLS = ["id", "gender", "TotalCharges"]


class FeatureEngineer(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        tenure_bins: list = None,
        tenure_labels: list = None,
        addon_cols: list = None,
        auto_methods: list = None,
    ):
        self.tenure_bins = tenure_bins or TENURE_BINS
        self.tenure_labels = tenure_labels or TENURE_LABELS
        self.addon_cols = addon_cols or ADDON_COLS
        self.auto_methods = auto_methods or AUTO_PAYMENT_METHODS

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        if (
            "TotalCharges" in X.columns
            and "tenure" in X.columns
            and "MonthlyCharges" in X.columns
        ):
            X["tc_residual"] = X["TotalCharges"] - (X["tenure"] * X["MonthlyCharges"])
            X["monthly_to_total_ratio"] = X["MonthlyCharges"] / X[
                "TotalCharges"
            ].replace(0, float("nan"))
            X["monthly_to_total_ratio"] = X["monthly_to_total_ratio"].fillna(1.0)

        if "tenure" in X.columns:
            X["tenure_group"] = pd.cut(
                X["tenure"],
                bins=self.tenure_bins,
                labels=self.tenure_labels,
                right=True,
                include_lowest=True,
            ).astype(str)

        if "PaymentMethod" in X.columns:
            X["is_auto_payment"] = (
                X["PaymentMethod"].isin(self.auto_methods).astype(int)
            )

        addon_present = [c for c in self.addon_cols if c in X.columns]
        if addon_present:
            X["service_count"] = (X[addon_present] == "Yes").sum(axis=1)
            X["has_any_addon"] = (X["service_count"] > 0).astype(int)

        return X

    def get_feature_names_out(self, input_features=None):
        return input_features


class ColumnDropper(BaseEstimator, TransformerMixin):
    def __init__(self, cols_to_drop: list = None):
        self.cols_to_drop = cols_to_drop or DROP_COLS

    def fit(self, X, y=None):
        self.cols_dropped_ = [c for c in self.cols_to_drop if c in X.columns]
        return self

    def transform(self, X):
        return X.drop(columns=self.cols_dropped_, errors="ignore")

    def get_feature_names_out(self, input_features=None):
        if input_features is None:
            return None
        return [f for f in input_features if f not in self.cols_dropped_]
