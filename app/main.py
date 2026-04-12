# app/main.py
"""
Entry point untuk Streamlit UI — TCCP Customer Churn Prediction.
Mengatur page config, sidebar, navigasi, dan halaman utama.
"""

import streamlit as st

from components.api_client import check_health

# Task 2.1.1 — page config harus menjadi perintah Streamlit pertama
st.set_page_config(
    page_title="TCCP — Churn Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Task 2.1.2 — Sidebar: navigasi + API status
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("TCCP Churn Predictor")
    st.caption("Telco Customer Churn Prediction System")
    st.divider()

    st.subheader("Navigation")
    st.page_link("main.py", label="🏠 Home")
    st.page_link("pages/prediction.py", label="🔍 Single Prediction")
    st.page_link("pages/batch_prediction.py", label="📂 Batch Prediction")
    st.page_link("pages/analytics.py", label="📈 Analytics")

    st.divider()

    st.subheader("API Status")
    health = check_health()

    if health is not None and health.get("status") == "healthy":
        model_version = health.get("model_version", "unknown")
        st.markdown(f"🟢 **API Connected**  \n`{model_version}`")
    elif health is not None and health.get("status") == "degraded":
        st.markdown("🟡 **API Degraded**")
    else:
        st.markdown("🔴 **API Unreachable**")

# ---------------------------------------------------------------------------
# Task 2.1.3 — Halaman utama (home page)
# ---------------------------------------------------------------------------
st.title("Customer Churn Prediction")

st.markdown(
    """
    Aplikasi ini memprediksi kemungkinan pelanggan telekomunikasi berhenti berlangganan (*churn*)
    menggunakan model machine learning yang telah dilatih dengan data historis pelanggan.

    Pilih salah satu mode prediksi di bawah, atau gunakan sidebar untuk navigasi langsung.
    """
)

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🔍 Single Prediction")
    st.markdown(
        """
        Masukkan data satu pelanggan secara manual dan dapatkan prediksi churn beserta
        penjelasan berbasis SHAP yang menunjukkan faktor pendorong utama.
        """
    )
    st.page_link("pages/prediction.py", label="Buka Single Prediction →")

with col2:
    st.subheader("📂 Batch Prediction")
    st.markdown(
        """
        Upload file CSV berisi banyak pelanggan sekaligus. Unduh template CSV,
        isi datanya, lalu jalankan prediksi massal dan ekspor hasilnya.
        """
    )
    st.page_link("pages/batch_prediction.py", label="Buka Batch Prediction →")

with col3:
    st.subheader("📈 Analytics")
    st.markdown(
        """
        Lihat performa model, visualisasi SHAP global, feature importance,
        dan distribusi hasil prediksi dari sesi batch terakhir.
        """
    )
    st.page_link("pages/analytics.py", label="Buka Analytics →")
