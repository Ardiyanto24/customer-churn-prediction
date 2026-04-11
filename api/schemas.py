# api/schemas.py

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List


class CustomerInput(BaseModel):
    """
    Schema input untuk satu baris data pelanggan yang akan diprediksi potensi churn-nya.
    Catatan: Kolom 'id' sengaja tidak disertakan di sini karena di-drop sebelum masuk preprocessing,
    dan kolom 'Churn' (target) tentu tidak ada saat inference.
    """

    # Demografi
    gender: Literal["Male", "Female"]
    SeniorCitizen: int = Field(
        ge=0, le=1, description="1 jika pelanggan adalah lansia, 0 jika tidak"
    )
    Partner: Literal["Yes", "No"]
    Dependents: Literal["Yes", "No"]

    # Layanan
    tenure: int = Field(ge=1, le=72, description="Lama berlangganan dalam bulan (1-72)")
    PhoneService: Literal["Yes", "No"]
    MultipleLines: Literal["Yes", "No", "No phone service"]
    InternetService: Literal["DSL", "Fiber optic", "No"]

    # Add-ons
    OnlineSecurity: Literal["Yes", "No", "No internet service"]
    OnlineBackup: Literal["Yes", "No", "No internet service"]
    DeviceProtection: Literal["Yes", "No", "No internet service"]
    TechSupport: Literal["Yes", "No", "No internet service"]
    StreamingTV: Literal["Yes", "No", "No internet service"]
    StreamingMovies: Literal["Yes", "No", "No internet service"]

    # Billing
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: Literal["Yes", "No"]
    PaymentMethod: Literal[
        "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
    ]
    MonthlyCharges: float = Field(ge=0.0, description="Tagihan bulanan dalam USD")
    TotalCharges: float = Field(ge=0.0, description="Total tagihan selama berlangganan")

    # Konfigurasi contoh untuk Swagger UI
    model_config = {
        "json_schema_extra": {
            "example": {
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "tenure": 2,
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "Yes",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
                "MonthlyCharges": 85.50,
                "TotalCharges": 171.00,
            }
        }
    }


class PredictionResult(BaseModel):
    """Hasil prediksi untuk satu pelanggan."""

    churn_prediction: bool
    churn_probability: float = Field(ge=0.0, le=1.0, description="Probabilitas churn (0.0 - 1.0)")
    risk_level: str = Field(description="'high' (>= 0.7), 'medium' (>= 0.4), atau 'low' (< 0.4)")
    shap_values: Optional[Dict[str, float]] = None


class PredictionResponse(BaseModel):
    """Response untuk endpoint prediksi tunggal (/predict)."""

    status: str = "success"
    model_version: str
    result: PredictionResult


class BatchPredictionItem(BaseModel):
    """Representasi satu item hasil dalam prediksi massal."""

    index: int
    result: PredictionResult


class BatchPredictionResponse(BaseModel):
    """Response untuk endpoint prediksi massal (/predict/batch)."""

    status: str = "success"
    model_version: str
    total_input: int
    total_predicted: int
    results: List[BatchPredictionItem]


class HealthResponse(BaseModel):
    """Response untuk endpoint health check (/health)."""

    status: str = Field(
        description="'healthy' jika semua artifact dimuat, 'degraded' jika ada yang gagal"
    )
    model_loaded: bool
    preprocessor_loaded: bool
    model_version: str
    uptime_seconds: float
