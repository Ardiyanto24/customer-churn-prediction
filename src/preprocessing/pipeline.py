# src/preprocessing/pipeline.py

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler


class ScalerWrapper(BaseEstimator, TransformerMixin):
    NUMERIC_TARGET_COLS = [
        'tenure', 'MonthlyCharges',
        'tc_residual', 'monthly_to_total_ratio'
    ]

    def __init__(self, cols: list = None):
        self.cols = cols or self.NUMERIC_TARGET_COLS
        self._scaler = StandardScaler()

    def fit(self, X, y=None):
        self.cols_present_ = [c for c in self.cols if c in X.columns]
        if self.cols_present_:
            self._scaler.fit(X[self.cols_present_])
        return self

    def transform(self, X):
        X = X.copy()
        if self.cols_present_:
            X[self.cols_present_] = self._scaler.transform(X[self.cols_present_])
        return X

    def get_feature_names_out(self, input_features=None):
        return input_features


class PreprocessingPipeline(BaseEstimator, TransformerMixin):
    def __init__(self):
        from src.preprocessing.feature_engineering import FeatureEngineer, ColumnDropper
        from src.preprocessing.encoders import StructuralEncoder, BinaryEncoder, OHEWrapper

        self.feature_engineer_ = FeatureEngineer()
        self.col_dropper_ = ColumnDropper()
        self.structural_encoder_ = StructuralEncoder()
        self.binary_encoder_ = BinaryEncoder()
        self.ohe_wrapper_ = OHEWrapper()
        self.scaler_wrapper_ = ScalerWrapper()

        self._steps = [
            ('feature_engineer', self.feature_engineer_),
            ('col_dropper', self.col_dropper_),
            ('structural_encoder', self.structural_encoder_),
            ('binary_encoder', self.binary_encoder_),
            ('ohe_wrapper', self.ohe_wrapper_),
            ('scaler_wrapper', self.scaler_wrapper_),
        ]

    def fit(self, X, y=None):
        X_transformed = X.copy()
        for name, step in self._steps:
            X_transformed = step.fit_transform(X_transformed, y)
        return self

    def transform(self, X):
        X_transformed = X.copy()
        for name, step in self._steps:
            X_transformed = step.transform(X_transformed)
        return X_transformed

    def get_feature_names_out(self, input_features=None):
        return input_features
