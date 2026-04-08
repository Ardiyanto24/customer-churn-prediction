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