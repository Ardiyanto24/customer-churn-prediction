# src/preprocessing/pipeline.py

from sklearn.base import BaseEstimator, TransformerMixin


class PreprocessingPipeline(BaseEstimator, TransformerMixin):
    """
    Kerangka class untuk PreprocessingPipeline.
    Dibutuhkan sebagai 'cetakan' agar joblib bisa memuat ulang (unpickle)
    pipeline yang disimpan dari Jupyter Notebook.
    """

    def __init__(self):
        # Saat di-load oleh joblib, atribut internal (seperti self.pipeline)
        # akan otomatis terisi dengan sendirinya dari file biner.
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        """
        Menjalankan transformasi.
        Mencoba memanggil atribut internal yang menyimpan pipeline asli.
        """
        # Mencari atribut yang menyimpan pipeline sklearn (biasanya bernama 'pipeline' atau 'preprocessor')
        for attr_name in ["pipeline", "preprocessor", "model", "_pipeline"]:
            if hasattr(self, attr_name):
                pipeline_obj = getattr(self, attr_name)
                if hasattr(pipeline_obj, "transform"):
                    return pipeline_obj.transform(X)

        # Jika notebook tidak menggunakan wrapper atribut, kembalikan X apa adanya
        return X

    def get_feature_names_out(self, input_features=None):
        """
        Meneruskan panggilan get_feature_names_out ke pipeline internal
        agar fungsi SHAP kita di predictor.py bisa berjalan.
        """
        for attr_name in ["pipeline", "preprocessor", "model", "_pipeline"]:
            if hasattr(self, attr_name):
                pipeline_obj = getattr(self, attr_name)
                if hasattr(pipeline_obj, "get_feature_names_out"):
                    return pipeline_obj.get_feature_names_out(input_features)

        # Fallback jika tidak ditemukan
        return input_features
