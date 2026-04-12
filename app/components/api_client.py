# app/components/api_client.py
"""
HTTP client untuk komunikasi antara Streamlit UI dan FastAPI.
Semua request ke API melalui modul ini — app/ tidak boleh memanggil
endpoint secara langsung di luar modul ini.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from config import settings
from src.utils.logger import get_logger

logger = get_logger("app.api_client")

API_BASE_URL: str = settings.API_BASE_URL


def check_health() -> Optional[Dict[str, Any]]:
    """
    Mengirim GET /health ke FastAPI.

    Returns:
        dict dari response JSON jika berhasil.
        None jika koneksi ditolak, timeout, atau error HTTP apapun.
    """
    try:
        response = httpx.get(f"{API_BASE_URL}/health", timeout=5.0)
        response.raise_for_status()
        return response.json()
    except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError):
        return None


def predict_single(customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mengirim POST /predict dengan satu CustomerInput.

    Args:
        customer_data: dict berisi field CustomerInput.

    Returns:
        dict response JSON jika status 200.
        dict dengan key "error" dan detail validasi jika status 422.
        dict dengan key "error" dan pesan model belum siap jika status 503.
        dict dengan key "error" dan pesan generik untuk error lainnya.
    """
    try:
        response = httpx.post(
            f"{API_BASE_URL}/predict",
            json=customer_data,
            timeout=30.0,
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            try:
                detail = response.json().get("detail", "Validation error")
            except Exception:
                detail = "Validation error"
            return {"error": detail}
        elif response.status_code == 503:
            return {"error": "Model belum siap. Coba beberapa saat lagi."}
        else:
            response.raise_for_status()
    except httpx.ConnectError:
        logger.error("predict_single: cannot connect to API at %s", API_BASE_URL)
        return {"error": "Tidak dapat terhubung ke API server."}
    except httpx.TimeoutException:
        logger.error("predict_single: request timed out")
        return {"error": "Request timeout. Coba lagi."}
    except httpx.HTTPStatusError as exc:
        logger.error("predict_single: HTTP error %s", exc)
        return {"error": f"API error: {exc.response.status_code}"}
    except Exception as exc:
        logger.error("predict_single: unexpected error %s", exc)
        return {"error": "Terjadi error yang tidak terduga."}


def predict_batch_json(customers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Mengirim POST /predict/batch dengan list CustomerInput (JSON).

    Args:
        customers: list of customer dicts.

    Returns:
        dict response JSON jika status 200.
        dict dengan key "error" untuk semua kondisi gagal.
    """
    try:
        response = httpx.post(
            f"{API_BASE_URL}/predict/batch",
            json=customers,
            timeout=120.0,
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            try:
                detail = response.json().get("detail", "Validation error")
            except Exception:
                detail = "Validation error"
            return {"error": detail}
        elif response.status_code == 503:
            return {"error": "Model belum siap. Coba beberapa saat lagi."}
        else:
            response.raise_for_status()
    except httpx.ConnectError:
        logger.error("predict_batch_json: cannot connect to API at %s", API_BASE_URL)
        return {"error": "Tidak dapat terhubung ke API server."}
    except httpx.TimeoutException:
        logger.error("predict_batch_json: request timed out")
        return {"error": "Request timeout. Coba lagi."}
    except httpx.HTTPStatusError as exc:
        logger.error("predict_batch_json: HTTP error %s", exc)
        return {"error": f"API error: {exc.response.status_code}"}
    except Exception as exc:
        logger.error("predict_batch_json: unexpected error %s", exc)
        return {"error": "Terjadi error yang tidak terduga."}


def predict_batch_csv(csv_bytes: bytes, filename: str = "batch.csv") -> Dict[str, Any]:
    """
    Mengirim POST /predict/batch-csv dengan file CSV sebagai multipart/form-data.

    Args:
        csv_bytes: isi file CSV dalam bytes (dari st.file_uploader.read()).
        filename: nama file yang dikirim ke API.

    Returns:
        dict response JSON jika status 200.
        dict dengan key "error" untuk semua kondisi gagal.
    """
    try:
        response = httpx.post(
            f"{API_BASE_URL}/predict/batch-csv",
            files={"file": (filename, csv_bytes, "text/csv")},
            timeout=120.0,
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 422:
            try:
                detail = response.json().get("detail", "Validation error")
            except Exception:
                detail = "Validation error"
            return {"error": detail}
        elif response.status_code == 503:
            return {"error": "Model belum siap. Coba beberapa saat lagi."}
        else:
            response.raise_for_status()
    except httpx.ConnectError:
        logger.error("predict_batch_csv: cannot connect to API at %s", API_BASE_URL)
        return {"error": "Tidak dapat terhubung ke API server."}
    except httpx.TimeoutException:
        logger.error("predict_batch_csv: request timed out")
        return {"error": "Request timeout. Coba lagi."}
    except httpx.HTTPStatusError as exc:
        logger.error("predict_batch_csv: HTTP error %s", exc)
        return {"error": f"API error: {exc.response.status_code}"}
    except Exception as exc:
        logger.error("predict_batch_csv: unexpected error %s", exc)
        return {"error": "Terjadi error yang tidak terduga."}
