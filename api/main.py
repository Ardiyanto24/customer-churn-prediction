# api/main.py

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.utils.logger import get_logger
from api.predictor import predictor
from config import settings

# Inisialisasi logger terpusat
logger = get_logger("api.main")

# Catat waktu mulai saat module di-load (untuk menghitung uptime_seconds)
_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler untuk mengelola state saat aplikasi mulai (startup) dan berhenti (shutdown).
    """
    logger.info("Aplikasi mulai. Mencoba memuat ML artifacts...")

    # Memuat model dan preprocessor HANYA SATU KALI saat API menyala
    success = predictor.load_artifacts(
        model_path=settings.MODEL_PATH, 
        preprocessor_path=settings.PREPROCESSOR_PATH
    )

    if success:
        logger.info("✅ Artifacts berhasil dimuat. API siap melayani prediksi.")
    else:
        logger.error("❌ Gagal memuat artifacts! API berjalan dalam mode degraded.")

    yield  # Pada titik ini aplikasi sedang berjalan melayani request

    # Dijalankan saat aplikasi menerima sinyal untuk berhenti
    logger.info("Aplikasi sedang shutdown. Membersihkan resources...")

# Inisialisasi instance aplikasi FastAPI
app = FastAPI(
    title="TCCP Churn Prediction API",
    description="REST API untuk prediksi churn pelanggan telekomunikasi. Menggunakan model yang dilatih dengan pipeline end-to-end mencakup EDA, XAI quality gate, dan hyperparameter tuning.",
    version="1.0.0",
    lifespan=lifespan
)

# Konfigurasi CORS Middleware
# Mengizinkan akses dari semua asal ("*") karena ini adalah read-only inference service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Menangkap semua unhandled exception untuk mencegah server crash dan
    memberikan balasan error 500 yang terstruktur.
    """
    logger.error(f"Terjadi unhandled exception pada endpoint {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )
