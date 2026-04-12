# app/components/shap_chart.py
"""
Streamlit component untuk menampilkan SHAP bar chart hasil prediksi.
Digunakan oleh halaman Single Prediction untuk visualisasi kontribusi fitur.
"""

from typing import Dict, Optional

import matplotlib.pyplot as plt
import streamlit as st


def render_shap_bar_chart(shap_values: Optional[Dict[str, float]]) -> None:
    """
    Render horizontal bar chart SHAP values ke Streamlit.

    Menampilkan top-10 fitur berdasarkan absolute SHAP value.
    Batang merah = kontribusi positif (mendorong ke churn).
    Batang biru  = kontribusi negatif (mendorong ke tidak churn).

    Args:
        shap_values: dict {nama_fitur: shap_value} atau None.

    Returns:
        None — fungsi ini hanya me-render ke UI.
    """
    if not shap_values:
        st.info("SHAP values tidak tersedia untuk prediksi ini.")
        return

    # Urutkan berdasarkan absolute value descending, ambil top-10
    sorted_items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:10]

    if not sorted_items:
        st.info("SHAP values tidak tersedia untuk prediksi ini.")
        return

    features = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    colors = ["#FF4B4B" if v > 0 else "#4B9EFF" for v in values]

    fig, ax = plt.subplots(figsize=(8, max(4, len(features) * 0.5)))

    ax.barh(features[::-1], values[::-1], color=colors[::-1])
    ax.axvline(x=0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("SHAP Value (impact on prediction)")
    ax.set_title("Feature Contributions")
    ax.tick_params(axis="y", labelsize=9)

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
