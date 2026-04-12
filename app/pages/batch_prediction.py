# app/pages/batch_prediction.py
"""
Halaman Batch Prediction — upload CSV pelanggan dan jalankan prediksi massal.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.components.api_client import predict_batch_csv  # noqa: E402

st.set_page_config(
    page_title="TCCP — Churn Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Batch Customer Prediction")
st.caption(
    "Upload file CSV berisi data pelanggan untuk diprediksi secara massal. "
    "CSV harus memiliki kolom: gender, SeniorCitizen, Partner, Dependents, tenure, "
    "PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, "
    "DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, "
    "PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges."
)

# ---------------------------------------------------------------------------
# Task 4.1.1 — File uploader
# ---------------------------------------------------------------------------
_TEMPLATE_COLUMNS = [
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
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
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
]

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"],
    help=(
        "Wajib ada kolom: gender, SeniorCitizen, Partner, Dependents, tenure, "
        "PhoneService, MultipleLines, InternetService, OnlineSecurity, OnlineBackup, "
        "DeviceProtection, TechSupport, StreamingTV, StreamingMovies, Contract, "
        "PaperlessBilling, PaymentMethod, MonthlyCharges, TotalCharges. "
        "Kolom id dan Churn akan diabaikan jika ada."
    ),
)

if uploaded_file is not None:
    st.session_state["uploaded_file"] = uploaded_file

# ---------------------------------------------------------------------------
# Task 4.1.2 — CSV preview + template download
# ---------------------------------------------------------------------------
st.download_button(
    label="Download Template CSV",
    data=",".join(_TEMPLATE_COLUMNS) + "\n",
    file_name="tccp_template.csv",
    mime="text/csv",
)

if (
    "uploaded_file" in st.session_state
    and st.session_state["uploaded_file"] is not None
):
    file_obj = st.session_state["uploaded_file"]

    try:
        file_obj.seek(0)
        preview_df = pd.read_csv(file_obj)

        st.subheader("Preview")
        st.dataframe(preview_df, use_container_width=True, height=200)

        col_info1, col_info2, col_info3 = st.columns(3)
        with col_info1:
            st.metric("Rows", len(preview_df))
        with col_info2:
            st.metric("Columns", len(preview_df.columns))
        with col_info3:
            st.caption("Detected columns:")
            st.caption(", ".join(preview_df.columns.tolist()))

    except Exception as exc:
        st.error(f"Gagal membaca CSV: {exc}")

    # ---------------------------------------------------------------------------
    # Task 4.2.1 — Run batch prediction button
    # ---------------------------------------------------------------------------
    if st.button("Run Batch Prediction", type="primary"):
        file_obj = st.session_state["uploaded_file"]
        csv_bytes = file_obj.getvalue()
        filename = file_obj.name if hasattr(file_obj, "name") else "batch.csv"

        with st.spinner("Running predictions..."):
            response = predict_batch_csv(csv_bytes, filename)

        if "error" in response:
            st.error(f"Prediksi gagal: {response['error']}")
        else:
            st.session_state["batch_results"] = response
            st.success(
                f"Selesai! {response.get('total_predicted', 0)} dari "
                f"{response.get('total_input', 0)} pelanggan diprediksi."
            )

# ---------------------------------------------------------------------------
# Task 4.2.2 — Results table with color highlight and download
# ---------------------------------------------------------------------------
if "batch_results" in st.session_state:
    batch_response = st.session_state["batch_results"]
    items = batch_response.get("results", [])

    if not items:
        st.info("Tidak ada hasil prediksi.")
    else:
        rows = []
        for item in items:
            result = item.get("result", {})
            rows.append(
                {
                    "index": item.get("index"),
                    "churn_prediction": result.get("churn_prediction"),
                    "churn_probability": round(result.get("churn_probability", 0.0), 4),
                    "risk_level": result.get("risk_level", ""),
                }
            )

        results_df = pd.DataFrame(rows)

        # Summary metrics
        st.divider()
        st.subheader("Results Summary")
        total = len(results_df)
        churned = int(results_df["churn_prediction"].sum())
        churn_rate = churned / total * 100 if total > 0 else 0.0

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Customers", total)
        with m2:
            st.metric("Predicted Churn", churned)
        with m3:
            st.metric("Churn Rate", f"{churn_rate:.1f}%")

        # Styled DataFrame
        def _highlight_risk(row: pd.Series) -> list:
            color = {
                "high": "background-color: #ffcccc",
                "medium": "background-color: #fff3cc",
                "low": "background-color: #ccffcc",
            }.get(str(row["risk_level"]).lower(), "")
            return [color] * len(row)

        styled = results_df.style.apply(_highlight_risk, axis=1)
        st.dataframe(styled, use_container_width=True)

        # Download results
        st.download_button(
            label="Download Predictions CSV",
            data=results_df.to_csv(index=False).encode("utf-8"),
            file_name="tccp_predictions.csv",
            mime="text/csv",
        )
