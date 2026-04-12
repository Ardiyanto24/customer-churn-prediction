# src/preprocessing/encoders.py

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import OneHotEncoder


class StructuralEncoder(BaseEstimator, TransformerMixin):
    STRUCTURAL_MAP = {
        'Yes'                : 1,
        'No'                 : 0,
        'No internet service': -1,
        'No phone service'   : -1,
    }

    def __init__(self, cols: list = None):
        self.cols = cols

    def fit(self, X, y=None):
        self.cols_present_ = [c for c in (self.cols or []) if c in X.columns]
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.cols_present_:
            X[col] = X[col].map(self.STRUCTURAL_MAP).fillna(X[col])
        return X

    def get_feature_names_out(self, input_features=None):
        return input_features


class BinaryEncoder(BaseEstimator, TransformerMixin):
    BINARY_MAP = {'Yes': 1, 'No': 0}

    def __init__(self, cols: list = None):
        self.cols = cols

    def fit(self, X, y=None):
        self.cols_present_ = [c for c in (self.cols or []) if c in X.columns]
        return self

    def transform(self, X):
        X = X.copy()
        for col in self.cols_present_:
            X[col] = X[col].map(self.BINARY_MAP).fillna(X[col])
        return X

    def get_feature_names_out(self, input_features=None):
        return input_features


class OHEWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, cols: list = None):
        self.cols = cols
        self._encoder = OneHotEncoder(
            drop='first',
            sparse_output=False,
            handle_unknown='ignore',
            dtype=np.float64
        )

    def fit(self, X, y=None):
        self.cols_present_ = [c for c in (self.cols or []) if c in X.columns]
        if self.cols_present_:
            self._encoder.fit(X[self.cols_present_])
            self.ohe_feature_names_ = self._encoder.get_feature_names_out(
                self.cols_present_
            ).tolist()
        else:
            self.ohe_feature_names_ = []
        return self

    def transform(self, X):
        X = X.copy()
        if not self.cols_present_:
            return X
        ohe_array = self._encoder.transform(X[self.cols_present_])
        ohe_df = pd.DataFrame(
            ohe_array,
            columns=self.ohe_feature_names_,
            index=X.index
        )
        X = X.drop(columns=self.cols_present_)
        X = pd.concat([X, ohe_df], axis=1)
        return X

    def get_feature_names_out(self, input_features=None):
        return input_features
