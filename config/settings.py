import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

# =============================================================================
# DATA AND COLUMN CONSTANTS
# =============================================================================

# Target and ID Columns
TARGET_COLUMN = "Churn"
ID_COLUMN = "id"
CHURN_POSITIVE_LABEL = "Yes"
CHURN_NEGATIVE_LABEL = "No"

# Numeric Columns
NUMERIC_COLS = [
    "tenure", 
    "MonthlyCharges", 
    "TotalCharges"
]

# Categorical Columns (Excluding Target)
CATEGORICAL_COLS = [
    "gender", 
    "SeniorCitizen", 
    "Partner", 
    "Dependents", 
    "PhoneService", 
    "MultipleLines", 
    "InternetService", 
    "OnlineSecurity", 
    "OnlineBackup", 
    "DeviceProtection", 
    "TechSupport", 
    "StreamingTV", 
    "StreamingMovies", 
    "Contract", 
    "PaperlessBilling", 
    "PaymentMethod"
]

# Internet Add-on Columns
ADDON_COLS = [
    "OnlineSecurity", 
    "OnlineBackup", 
    "DeviceProtection", 
    "TechSupport", 
    "StreamingTV", 
    "StreamingMovies"
]

# Structural Values (Not Missing Values)
NO_INTERNET_VALUE = "No internet service"
NO_PHONE_VALUE = "No phone service"

# =============================================================================
# SPLIT AND REPRODUCIBILITY CONSTANTS
# =============================================================================

# Seed yang digunakan untuk semua operasi random agar hasil konsisten
RANDOM_SEED = 42

# Proporsi pembagian dataset
TEST_SIZE = 0.15   # 15% untuk test set dari total data
VAL_SIZE = 0.15    # 15% untuk validation set dari sisa training data

# =============================================================================
# XAI QUALITY GATE CONSTANTS
# =============================================================================
# Konstanta ini mendefinisikan kriteria untuk memutuskan apakah sebuah model 
# layak (pass) untuk dilanjutkan ke tahap berikutnya berdasarkan analisis SHAP.

# Fitur yang diharapkan masuk ke jajaran top features berdasarkan domain knowledge.
# List ini berasal dari hasil EDA Fase 6 (EarlyWarningCompiler) yang merupakan 
# fitur dengan bukti kuantitatif terkuat terhadap churn.
EXPECTED_IMPORTANT_FEATURES = [
    "Contract", 
    "tenure", 
    "MonthlyCharges", 
    "TotalCharges", 
    "InternetService"
]

# Jumlah fitur teratas yang dievaluasi dari SHAP feature importance
XAI_TOP_N_FEATURES = 10

# Ambang batas minimal proporsi overlap (0.5 berarti minimal 50%)
# Contoh: Minimal 3 dari 5 expected features harus masuk ke dalam top-10 SHAP.
XAI_MIN_OVERLAP = 0.5