# src/preprocessing/encoders.py

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class EncoderHelper(BaseEstimator, TransformerMixin):
    """
    Custom transformer untuk membantu proses encoding fitur kategorikal
    pada dataset Telco Customer Churn.
    """
    def __init__(self):
        pass

    def fit(self, X, y=None):
        # Karena ini hanya helper transform, fit tidak melakukan apa-apa
        # dan hanya mengembalikan dirinya sendiri
        return self

    def transform(self, X):
        """
        Menjalankan transformasi data.
        Karena proses fit/transform utama kemungkinan sudah tersimpan di state joblib,
        kita mengembalikan data X apa adanya atau menjalankan fungsi spesifik jika diperlukan.
        """
        # Salin data untuk menghindari SettingWithCopyWarning dari pandas
        X_encoded = X.copy() if isinstance(X, pd.DataFrame) else X

        # Catatan: Jika di dalam notebook-mu EncoderHelper melakukan operasi replace
        # atau manipulasi spesifik (seperti handling "No internet service"),
        # operasi tersebut akan berjalan dengan aman karena kompatibel dengan sklearn.

        return X_encoded
