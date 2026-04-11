import pandas as pd
from pathlib import Path
from typing import List, Union, Any

from src.utils.logger import get_logger
from src.utils.serialization import load_artifact
from api.schemas import CustomerInput

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
            # Menggunakan utilitas yang kita buat di Step 1
            self._preprocessor = load_artifact(preprocessor_path, logger)
            self._model = load_artifact(model_path, logger)

            # Ekstrak nama file model sebagai versi
            self._model_version = Path(model_path).name
            self._is_ready = True

            logger.info("✅ Semua artifact berhasil dimuat. Predictor siap digunakan.")
            return True

        except Exception as e:
            self._is_ready = False
            logger.error(f"❌ Gagal memuat artifact. API berjalan dalam degraded mode. Error: {e}")
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
