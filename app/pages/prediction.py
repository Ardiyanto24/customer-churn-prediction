# app/pages/prediction.py
"""
Halaman Single Prediction — input satu pelanggan dan tampilkan hasil prediksi churn.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.components.api_client import predict_single
from app.components.result_card import render_result_card
from app.components.shap_chart import render_shap_bar_chart

st.set_page_config(
    page_title="TCCP — Churn Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Single Customer Prediction")
st.caption(
    "Masukkan data satu pelanggan, lalu klik **Predict Churn** untuk mendapatkan "
    "prediksi beserta penjelasan SHAP."
)

# ---------------------------------------------------------------------------
# Task 3.1.2 — 20 input fields in 3 columns (inside form)
# ---------------------------------------------------------------------------
with st.form(key="prediction_form"):
    col1, col2, col3 = st.columns(3)

    # --- Kolom 1: Demografi & Layanan Dasar ---
    with col1:
        st.subheader("Demografi & Layanan Dasar")
        gender = st.selectbox("Gender", options=["Male", "Female"])
        senior_citizen = st.selectbox(
            "Senior Citizen",
            options=[0, 1],
            format_func=lambda x: "No (0)" if x == 0 else "Yes (1)",
        )
        partner = st.selectbox("Partner", options=["Yes", "No"])
        dependents = st.selectbox("Dependents", options=["Yes", "No"])
        tenure = st.slider("Tenure (months)", min_value=1, max_value=72, value=12)
        phone_service = st.selectbox("Phone Service", options=["Yes", "No"])
        multiple_lines = st.selectbox(
            "Multiple Lines", options=["Yes", "No", "No phone service"]
        )

    # --- Kolom 2: Internet & Add-on ---
    with col2:
        st.subheader("Internet & Add-on Services")
        internet_service = st.selectbox(
            "Internet Service", options=["DSL", "Fiber optic", "No"]
        )
        online_security = st.selectbox(
            "Online Security", options=["Yes", "No", "No internet service"]
        )
        online_backup = st.selectbox(
            "Online Backup", options=["Yes", "No", "No internet service"]
        )
        device_protection = st.selectbox(
            "Device Protection", options=["Yes", "No", "No internet service"]
        )
        tech_support = st.selectbox(
            "Tech Support", options=["Yes", "No", "No internet service"]
        )
        streaming_tv = st.selectbox(
            "Streaming TV", options=["Yes", "No", "No internet service"]
        )
        streaming_movies = st.selectbox(
            "Streaming Movies", options=["Yes", "No", "No internet service"]
        )

    # --- Kolom 3: Billing ---
    with col3:
        st.subheader("Billing")
        contract = st.selectbox(
            "Contract", options=["Month-to-month", "One year", "Two year"]
        )
        paperless_billing = st.selectbox("Paperless Billing", options=["Yes", "No"])
        payment_method = st.selectbox(
            "Payment Method",
            options=[
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
        )
        monthly_charges = st.number_input(
            "Monthly Charges (USD)",
            min_value=0.0,
            max_value=200.0,
            value=65.0,
            step=0.01,
        )
        total_charges = st.number_input(
            "Total Charges (USD)",
            min_value=0.0,
            value=1500.0,
            step=0.01,
        )

    submitted = st.form_submit_button("Predict Churn", type="primary")

# ---------------------------------------------------------------------------
# Task 3.2.1 — Submit logic: collect form → call API → store in session_state
# ---------------------------------------------------------------------------
if submitted:
    customer_data = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
    }

    with st.spinner("Menghubungi API..."):
        response = predict_single(customer_data)

    if "error" in response:
        st.error(f"Prediksi gagal: {response['error']}")
    else:
        st.session_state["last_prediction"] = response

# ---------------------------------------------------------------------------
# Task 3.2.2 — Result rendering: result_card + shap_chart + raw JSON expander
# ---------------------------------------------------------------------------
if "last_prediction" in st.session_state:
    prediction_response = st.session_state["last_prediction"]
    result = prediction_response.get("result", {})

    st.divider()
    st.subheader("Prediction Result")

    left_col, right_col = st.columns([0.4, 0.6])

    with left_col:
        render_result_card(result)

    with right_col:
        render_shap_bar_chart(result.get("shap_values"))

    with st.expander("See raw API response"):
        st.json(prediction_response)
