# app/pages/analytics.py
"""
Halaman Analytics — model status, XAI visualizations, dan distribusi batch prediction.
app/ diizinkan membaca file statis dari reports/xai_reports/ (exception di CLAUDE.md).
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.components.api_client import check_health  # noqa: E402

st.set_page_config(
    page_title="TCCP — Churn Predictor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Model Analytics & Insights")
st.caption(
    "Halaman ini menampilkan informasi model aktif, visualisasi XAI dari proses training, "
    "dan distribusi hasil batch prediction terakhir."
)

# Path ke folder XAI reports (pathlib — tidak ada string concatenation)
_XAI_DIR = Path(__file__).resolve().parent.parent.parent / "reports" / "xai_reports"

# ---------------------------------------------------------------------------
# Task 5.1.1 — Model Status section
# ---------------------------------------------------------------------------
st.subheader("Model Status")

health = check_health()

if health is not None:
    model_version = health.get("model_version", "unknown")
    uptime_seconds = health.get("uptime_seconds", 0) or 0

    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    col_v, col_u = st.columns(2)
    with col_v:
        st.metric("Model Version", model_version)
    with col_u:
        st.metric("Uptime", uptime_str)
else:
    st.warning("API tidak tersedia saat ini. Informasi model tidak dapat ditampilkan.")

st.divider()

# ---------------------------------------------------------------------------
# Task 5.2.1 — Global Feature Importance (3 tabs)
# ---------------------------------------------------------------------------
st.subheader("Global Feature Importance")

tab_shap, tab_perm, tab_builtin = st.tabs(
    ["SHAP Summary", "Permutation Importance", "Built-in Importance"]
)

with tab_shap:
    shap_file = _XAI_DIR / "shap_summary.png"
    if shap_file.exists():
        st.image(
            str(shap_file),
            use_column_width=True,
            caption="SHAP Summary Plot — kontribusi global setiap fitur terhadap prediksi churn.",
        )
    else:
        st.info(
            "File `shap_summary.png` belum ditemukan di `reports/xai_reports/`. "
            "Jalankan notebook XAI di Kaggle terlebih dahulu untuk menghasilkan visualisasi ini."
        )

with tab_perm:
    perm_file = _XAI_DIR / "permutation_importance.png"
    if perm_file.exists():
        st.image(
            str(perm_file),
            use_column_width=True,
            caption="Permutation Feature Importance — penurunan performa model saat setiap fitur diacak.",
        )
    else:
        st.info(
            "File `permutation_importance.png` belum ditemukan di `reports/xai_reports/`. "
            "Jalankan notebook XAI di Kaggle terlebih dahulu untuk menghasilkan visualisasi ini."
        )

with tab_builtin:
    builtin_files = (
        [
            f
            for f in _XAI_DIR.glob("*.png")
            if "builtin" in f.name.lower() or "feature_importance" in f.name.lower()
        ]
        if _XAI_DIR.exists()
        else []
    )

    if builtin_files:
        st.image(
            str(builtin_files[0]),
            use_column_width=True,
            caption="Built-in Feature Importance — importance dari model tree-based secara internal.",
        )
    else:
        st.info(
            "File built-in importance belum ditemukan di `reports/xai_reports/`. "
            "Cari file PNG dengan nama mengandung `builtin` atau `feature_importance`. "
            "Jalankan notebook XAI di Kaggle terlebih dahulu."
        )

# ---------------------------------------------------------------------------
# Task 5.2.2 — SHAP Force Plot expander
# ---------------------------------------------------------------------------
with st.expander("SHAP Force Plot (HTML)"):
    force_plot_file = _XAI_DIR / "shap_force_plot.html"
    if force_plot_file.exists():
        html_content = force_plot_file.read_text(encoding="utf-8")
        components.html(html_content, height=200)
    else:
        st.info(
            "File `shap_force_plot.html` belum ditemukan di `reports/xai_reports/`. "
            "Jalankan notebook XAI di Kaggle terlebih dahulu."
        )

st.divider()

# ---------------------------------------------------------------------------
# Task 5.3.1 — Batch Prediction Distribution dari session state
# ---------------------------------------------------------------------------
st.subheader("Batch Prediction Distribution")

batch_results = st.session_state.get("batch_results")

if batch_results is not None:
    items = batch_results.get("results", [])

    if not items:
        st.info("Hasil batch kosong.")
    else:
        rows = [
            {
                "risk_level": item.get("result", {}).get("risk_level", ""),
                "churn_probability": item.get("result", {}).get(
                    "churn_probability", 0.0
                ),
            }
            for item in items
        ]
        dist_df = pd.DataFrame(rows)

        chart_col1, chart_col2, chart_col3 = st.columns(3)

        with chart_col1:
            risk_counts = dist_df["risk_level"].value_counts()
            colors = [
                {"high": "#FF4B4B", "medium": "#FFA500", "low": "#21C354"}.get(
                    k, "#CCCCCC"
                )
                for k in risk_counts.index
            ]
            fig1, ax1 = plt.subplots()
            ax1.pie(
                risk_counts.values,
                labels=risk_counts.index,
                colors=colors,
                autopct="%1.1f%%",
                startangle=90,
            )
            ax1.set_title("Risk Level Distribution")
            st.pyplot(fig1)
            plt.close(fig1)

        with chart_col2:
            fig2, ax2 = plt.subplots()
            ax2.hist(
                dist_df["churn_probability"],
                bins=20,
                color="#4B9EFF",
                edgecolor="white",
            )
            ax2.set_xlabel("Churn Probability")
            ax2.set_ylabel("Count")
            ax2.set_title("Churn Probability Distribution")
            st.pyplot(fig2)
            plt.close(fig2)

        with chart_col3:
            risk_order = ["low", "medium", "high"]
            ordered_counts = (
                dist_df["risk_level"].value_counts().reindex(risk_order, fill_value=0)
            )
            bar_colors = ["#21C354", "#FFA500", "#FF4B4B"]
            fig3, ax3 = plt.subplots()
            ax3.bar(ordered_counts.index, ordered_counts.values, color=bar_colors)
            ax3.set_xlabel("Risk Level")
            ax3.set_ylabel("Count")
            ax3.set_title("Predictions by Risk Level")
            st.pyplot(fig3)
            plt.close(fig3)
else:
    st.info(
        "Belum ada hasil batch prediction. "
        "Buka halaman **Batch Prediction**, upload CSV, dan jalankan prediksi terlebih dahulu."
    )
