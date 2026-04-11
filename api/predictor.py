# api/predictor.py

import sys
import time
import shap
import pandas as pd
from pathlib import Path
from typing import List, Union, Any, Dict, Optional

from src.utils.logger import get_logger
from src.utils.serialization import load_artifact
from api.schemas import CustomerInput, PredictionResult

# Inisialisasi logger terpusat
logger = get_logger("api.predictor")


class ModelPredictor:
    """
    Singleton class untuk mengelola state model dan preprocessor,
    serta menangani logika inference.
    """

    def __init__(self):
        self._model: Any = None
        self._preprocessor: Any = None
        self._model_version: str = "unknown"
        self._is_ready: bool = False

    def load_artifacts(self, model_path: Union[str, Path], preprocessor_path: Union[str, Path]) -> bool:
        """
        Memuat model dan preprocessor ke dalam memori.
        Jika gagal, aplikasi tidak crash (degraded mode).
        """
        try:
            # HACK: Menjembatani custom class dari Jupyter Notebook ke environment API
            try:
                from src.preprocessing.pipeline import PreprocessingPipeline
                sys.modules['__main__'].PreprocessingPipeline = PreprocessingPipeline
            except ImportError:
                pass  # Abaikan jika struktur file berbeda

            # Menggunakan utilitas yang kita buat di Step 1
            self._preprocessor = load_artifact(preprocessor_path, logger)
            self._model = load_artifact(model_path, logger)

            # Ekstrak nama file model sebagai versi
            self._model_version = Path(model_path).name
            self._is_ready = True

            # Emoji dihapus agar terminal Windows tidak crash
            logger.info("SUKSES: Semua artifact berhasil dimuat. Predictor siap digunakan.")
            return True

        except Exception as e:
            self._is_ready = False
            # Emoji dihapus agar terminal Windows tidak crash
            logger.error(f"GAGAL: Tidak dapat memuat artifact. API berjalan dalam degraded mode. Error: {e}")
            return False

    def _prepare_dataframe(self, inputs: Union[CustomerInput, List[CustomerInput]]) -> pd.DataFrame:
        """
        Mengonversi input Pydantic (tunggal atau batch) menjadi pandas DataFrame.
        Urutan kolom akan secara otomatis mengikuti urutan field di Pydantic schema.
        Kolom 'id' dan 'Churn' secara natural tidak ada karena tidak didefinisikan di schema.
        """
        # Konversi Pydantic model ke dictionary
        if isinstance(inputs, CustomerInput):
            data = [inputs.model_dump()]
        else:
            data = [item.model_dump() for item in inputs]

        # Ubah list of dictionaries menjadi DataFrame
        df = pd.DataFrame(data)

        return df


# Inisiasi instance tunggal (singleton) untuk digunakan di router FastAPI nanti
predictor = ModelPredictor()


def predict(self, input_data: CustomerInput) -> PredictionResult:
    """
    Menjalankan prediksi untuk satu data pelanggan.
    """
    if not self._is_ready:
        raise RuntimeError("Model dan preprocessor belum siap. Pastikan artifact sudah di-load.")

    # 1. Konversi ke DataFrame
    df = self._prepare_dataframe(input_data)

    # 2. Preprocessing (HANYA transform, TIDAK BOLEH fit_transform)
    X_transformed = self._preprocessor.transform(df)

    # 3. Dapatkan probabilitas dari model
    proba_array = self._model.predict_proba(X_transformed)
    churn_probability = float(
        proba_array[0][1]
    )  # Index 1 adalah probabilitas kelas positif (Churn=Yes)

    # 4. Tentukan hasil prediksi dan level risiko
    churn_prediction = bool(churn_probability >= 0.5)

    if churn_probability >= 0.7:
        risk_level = "high"
    elif churn_probability >= 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    # 5. Logging aman (tanpa PII/data sensitif)
    logger.info(
        f"Single predict | Probability: {churn_probability:.4f} | Risk: {risk_level} | Churn: {churn_prediction}"
    )

    return PredictionResult(
        churn_prediction=churn_prediction,
        churn_probability=round(churn_probability, 4),
        risk_level=risk_level,
        shap_values=None,  # SHAP akan diisi oleh fungsi terpisah jika diminta
    )


def predict_batch(self, inputs: List[CustomerInput]) -> List[PredictionResult]:
    """
    Menjalankan prediksi untuk banyak data pelanggan sekaligus (dioptimasi).
    """
    if not self._is_ready:
        raise RuntimeError("Model dan preprocessor belum siap. Pastikan artifact sudah di-load.")

    start_time = time.time()

    # 1. Konversi seluruh input menjadi satu DataFrame
    df = self._prepare_dataframe(inputs)

    # 2. Preprocessing sekaligus
    X_transformed = self._preprocessor.transform(df)

    # 3. Prediksi sekaligus
    proba_array = self._model.predict_proba(X_transformed)

    results = []
    churn_count = 0

    # 4. Parsing hasil ke dalam bentuk list of PredictionResult
    for proba in proba_array:
        churn_prob = float(proba[1])
        pred = bool(churn_prob >= 0.5)

        if churn_prob >= 0.7:
            risk = "high"
        elif churn_prob >= 0.4:
            risk = "medium"
        else:
            risk = "low"

        if pred:
            churn_count += 1

        results.append(
            PredictionResult(
                churn_prediction=pred,
                churn_probability=round(churn_prob, 4),
                risk_level=risk,
                shap_values=None,
            )
        )

    exec_time_ms = (time.time() - start_time) * 1000
    logger.info(
        f"Batch predict | Total Input: {len(inputs)} | Predicted Churn: {churn_count} | Time: {exec_time_ms:.2f} ms"
    )

    return results


def compute_shap(self, input_data: CustomerInput) -> Optional[Dict[str, float]]:
    """
    Menghitung SHAP values untuk interpretasi prediksi lokal.
    Mengembalikan dictionary berisi nama fitur asli dan absolute SHAP value-nya.
    """
    if not self._is_ready:
        return None

    try:
        # 1. Konversi ke DataFrame dan Transform
        df = self._prepare_dataframe(input_data)
        X_transformed = self._preprocessor.transform(df)

        # 2. Inisialisasi explainer dan komputasi nilai SHAP
        explainer = shap.Explainer(self._model)
        shap_values = explainer(X_transformed)

        # 3. Tangani variasi bentuk array SHAP (tergantung arsitektur model)
        vals = shap_values.values
        if len(vals.shape) == 3:
            # Jika 3D (n_samples, n_features, n_classes), ambil kelas positif (indeks 1)
            vals = vals[0, :, 1]
        elif len(vals.shape) == 2:
            # Jika 2D (n_samples, n_features), model langsung mengeluarkan log-odds
            vals = vals[0, :]
        else:
            vals = vals[0]

        # 4. Agregasi fitur yang sudah di-encode kembali ke fitur asli
        feature_names_out = self._preprocessor.get_feature_names_out()
        original_features = df.columns.tolist()

        # Inisiasi dictionary dengan nilai 0.0 untuk setiap fitur asli
        shap_dict = {feat: 0.0 for feat in original_features}

        # Jumlahkan nilai absolut SHAP berdasarkan prefix nama fiturnya
        for i, out_feat in enumerate(feature_names_out):
            for orig_feat in original_features:
                # Cek apakah nama fitur asli adalah bagian dari nama fitur yang di-encode
                if orig_feat in out_feat:
                    shap_dict[orig_feat] += abs(float(vals[i]))
                    break  # Pindah ke fitur hasil encode berikutnya

        # 5. Urutkan dari pengaruh yang paling besar (descending)
        sorted_shap = dict(sorted(shap_dict.items(), key=lambda item: item[1], reverse=True))

        return sorted_shap

    except Exception as e:
        # Jika komputasi gagal, tidak membuat crash. API akan mengembalikan shap_values=None
        logger.warning(f"Gagal menghitung SHAP values: {e}")
        return None
