# src/utils/serialization.py

import joblib
import logging
from pathlib import Path
from typing import Any, Optional


def save_artifact(
    obj: Any, path: str | Path, logger: Optional[logging.Logger] = None
) -> bool:
    """
    Menyimpan objek Python (seperti model atau preprocessor) ke dalam file menggunakan joblib.
    Folder parent akan dibuat secara otomatis jika belum ada.
    """
    file_path = Path(path)

    # Buat direktori parent jika belum ada
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        joblib.dump(obj, file_path)
        if logger:
            logger.info(f"Artifact berhasil disimpan ke: {file_path}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Gagal menyimpan artifact ke {file_path}: {e}")
        raise e


def load_artifact(path: str | Path, logger: Optional[logging.Logger] = None) -> Any:
    """
    Memuat objek Python dari file menggunakan joblib.
    Akan raise FileNotFoundError jika file tidak ditemukan.
    """
    file_path = Path(path)

    # Cek eksistensi file sebelum memuat
    if not file_path.exists():
        error_msg = f"Artifact tidak ditemukan di path: {file_path.absolute()}"
        if logger:
            logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    try:
        obj = joblib.load(file_path)
        if logger:
            logger.info(
                f"Artifact berhasil dimuat dari: {file_path} (Tipe: {type(obj).__name__})"
            )
        return obj
    except Exception as e:
        if logger:
            logger.error(f"Gagal memuat artifact dari {file_path}: {e}")
        raise e
