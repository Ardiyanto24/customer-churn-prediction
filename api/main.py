# api/main.py

import io
import time
import pandas as pd
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.utils.logger import get_logger
from api.predictor import predictor
from api.schemas import (
    HealthResponse, 
    CustomerInput, 
    PredictionResponse, 
    BatchPredictionItem, 
    BatchPredictionResponse
)
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


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint untuk mengecek status kesehatan API dan kesiapan model.
    Akan mengembalikan status HTTP 200 OK meskipun dalam mode degraded,
    agar load balancer tahu bahwa server/aplikasi utama tetap hidup.
    """
    is_ready = predictor._is_ready

    return HealthResponse(
        status="healthy" if is_ready else "degraded",
        model_loaded=predictor._model is not None,
        preprocessor_loaded=predictor._preprocessor is not None,
        model_version=predictor._model_version,
        uptime_seconds=time.time() - _start_time
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"], summary="Predict churn for a single customer")
async def predict_single(input_data: CustomerInput):
    """Menerima data satu pelanggan dan mengembalikan prediksi beserta nilai XAI (SHAP)."""
    if not predictor._is_ready:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Model belum siap menerima request. Coba lagi nanti."})

    try:
        # 1. Hitung SHAP (menjelaskan alasan prediksi)
        shap_values = predictor.compute_shap(input_data)

        # 2. Hitung Prediksi Utama
        prediction_result = predictor.predict(input_data)

        # 3. Gabungkan SHAP ke dalam hasil prediksi
        prediction_result.shap_values = shap_values

        return PredictionResponse(
            model_version=predictor._model_version,
            result=prediction_result
        )
    except Exception as e:
        logger.error(f"Error pada single prediction: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Terjadi kesalahan internal saat memproses prediksi."})


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"], summary="Predict churn for multiple customers (JSON)")
async def predict_batch_json(inputs: List[CustomerInput]):
    """Menerima array/list data pelanggan dalam format JSON dan mengembalikan prediksi batch."""
    if not predictor._is_ready:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Model belum siap menerima request."})

    if len(inputs) == 0:
        return JSONResponse(status_code=422, content={"status": "error", "message": "List input tidak boleh kosong."})

    if len(inputs) > 1000:
        return JSONResponse(status_code=422, content={"status": "error", "message": "Batas maksimum adalah 1000 pelanggan per request."})

    try:
        predictions = predictor.predict_batch(inputs)

        results = [
            BatchPredictionItem(index=i, result=pred)
            for i, pred in enumerate(predictions)
        ]

        # Hitung berapa banyak yang diprediksi akan churn
        churn_count = sum(1 for p in predictions if p.churn_prediction)

        return BatchPredictionResponse(
            model_version=predictor._model_version,
            total_input=len(inputs),
            total_predicted=churn_count,
            results=results
        )
    except Exception as e:
        logger.error(f"Error pada batch prediction JSON: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": "Terjadi kesalahan internal saat memproses prediksi massal."})


@app.post("/predict/batch-csv", response_model=BatchPredictionResponse, tags=["Prediction"], summary="Predict churn from CSV file upload")
async def predict_batch_csv(file: UploadFile = File(...)):
    """Menerima upload file CSV, memvalidasinya, dan mengembalikan prediksi batch."""
    if not predictor._is_ready:
        return JSONResponse(status_code=503, content={"status": "error", "message": "Model belum siap menerima request."})

    if not file.filename.endswith(".csv"):
        return JSONResponse(status_code=422, content={"status": "error", "message": "File harus berformat .csv"})

    try:
        # 1. Baca dan parsing file CSV di memori
        content = await file.read()
        decoded_content = content.decode("utf-8")
        df = pd.read_csv(io.StringIO(decoded_content))

        # 2. Cek apakah ada kolom wajib yang hilang
        required_cols = list(CustomerInput.model_fields.keys())
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            return JSONResponse(status_code=422, content={"status": "error", "message": f"Kolom wajib berikut hilang dari CSV: {missing_cols}"})

        # 3. Drop kolom id & Churn secara otomatis jika kebetulan ada
        cols_to_drop = [col for col in ["id", "Churn"] if col in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        # 4. Validasi baris per baris menggunakan schema Pydantic
        valid_inputs = []
        skipped_indices = []
        records = df.to_dict(orient="records")

        for i, record in enumerate(records):
            try:
                valid_inputs.append(CustomerInput(**record))
            except Exception:
                skipped_indices.append(i)  # Abaikan baris yang gagal validasi tipe/nilai

        if not valid_inputs:
            return JSONResponse(status_code=422, content={"status": "error", "message": "Tidak ada baris data yang valid di dalam file CSV."})

        if len(valid_inputs) > 1000:
            return JSONResponse(status_code=422, content={"status": "error", "message": "Batas maksimum data yang valid adalah 1000 baris per file CSV."})

        # 5. Lakukan prediksi massal
        predictions = predictor.predict_batch(valid_inputs)

        results = [
            BatchPredictionItem(index=i, result=pred)
            for i, pred in enumerate(predictions)
        ]

        churn_count = sum(1 for p in predictions if p.churn_prediction)

        # 6. Susun pesan status jika ada baris yang dilewati
        status_msg = "success"
        if skipped_indices:
            status_msg = f"success_with_warnings: melewati {len(skipped_indices)} baris tidak valid."
            logger.warning(f"File CSV {file.filename}: Baris dilewati (indeks): {skipped_indices}")

        return BatchPredictionResponse(
            status=status_msg,
            model_version=predictor._model_version,
            total_input=len(valid_inputs),
            total_predicted=churn_count,
            results=results
        )

    except Exception as e:
        logger.error(f"Error pada batch prediction CSV: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "message": f"Gagal memproses file CSV: {str(e)}"})


@app.get("/", tags=["General"], summary="Welcome Endpoint")
async def root():
    """
    Welcome endpoint. Memberikan informasi dasar tentang API dan navigasi ke dokumentasi.
    """
    return JSONResponse(
        content={
            "name": "TCCP Churn Prediction API",
            "version": "1.0.0",
            "message": "Welcome to the Telco Customer Churn Prediction REST API.",
            "docs": "/docs",
            "health": "/health"
        }
    )

if __name__ == "__main__":
    import uvicorn

    # Catatan: Untuk development dengan hot reload, gunakan perintah dari terminal:
    # uvicorn api.main:app --reload

    uvicorn.run(
        app="api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )
