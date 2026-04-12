# app/components/result_card.py
"""
Streamlit component untuk menampilkan hasil prediksi churn sebagai kartu visual.
Digunakan oleh halaman Single Prediction.
"""

import streamlit as st


def render_result_card(result: dict) -> None:
    """
    Render kartu hasil prediksi ke Streamlit.

    Args:
        result: dict dengan keys:
            - churn_prediction (bool): True jika diprediksi churn
            - churn_probability (float): probabilitas churn (0.0–1.0)
            - risk_level (str): "low", "medium", atau "high"
            - shap_values (dict | None): SHAP values per fitur

    Returns:
        None — fungsi ini hanya me-render ke UI.
    """
    risk_level = result.get("risk_level", "").lower()
    churn_probability = result.get("churn_probability", 0.0)
    churn_prediction = result.get("churn_prediction", False)

    # Tentukan warna badge berdasarkan risk_level
    badge_colors = {
        "high": ("#FF4B4B", "#FFFFFF"),
        "medium": ("#FFA500", "#FFFFFF"),
        "low": ("#21C354", "#FFFFFF"),
    }
    bg_color, text_color = badge_colors.get(risk_level, ("#CCCCCC", "#000000"))

    with st.container():
        # Badge risk level
        st.markdown(
            f"""
            <div style="display: inline-block; padding: 6px 18px; border-radius: 20px;
                        background-color: {bg_color}; color: {text_color};
                        font-weight: bold; font-size: 1rem; margin-bottom: 12px;">
                {risk_level.upper()} RISK
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Churn probability besar
        st.markdown(
            f"""
            <div style="font-size: 2.5rem; font-weight: bold; color: {bg_color};
                        line-height: 1.2; margin-bottom: 4px;">
                {churn_probability * 100:.1f}%
            </div>
            <div style="font-size: 0.9rem; color: #888888; margin-bottom: 16px;">
                Churn Probability
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Prediksi label
        if churn_prediction:
            st.markdown(
                "<div style='font-size: 1.1rem; font-weight: bold; color: #FF4B4B;'>"
                "⚠ Likely to Churn</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='font-size: 1.1rem; font-weight: bold; color: #21C354;'>"
                "✓ Likely to Stay</div>",
                unsafe_allow_html=True,
            )
