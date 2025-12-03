from typing import Optional

import streamlit as st
import pandas as pd

from forecasting_engine import run_forecast


# =============== CSS KHUSUS HALAMAN FORECASTING ===============
st.markdown("""
<style>
/* CARD UTAMA TENGAH */
.main-card {
    background-color: #111827;
    padding: 28px 34px 30px 34px;
    border-radius: 26px;
    max-width: 1000px;
    margin: 32px auto 40px auto;
    box-shadow: 0 22px 48px rgba(0, 0, 0, 0.65);
    border: 1px solid #1f2937;
}

/* Kartu kecil (Today Overview, Forecast Summary, Model Eval) */
.small-card {
    background-color: #252B31;
    padding: 18px 20px;
    border-radius: 16px;
}

/* Kartu besar bawah (chart + tabel) */
.bottom-card {
    background-color: #252B31;
    padding: 18px 20px;
    border-radius: 16px;
    height: 100%;
}

/* Empty state di tengah card */
.empty-card-wrapper {
    margin-top: 28px;
}
.empty-card {
    background-color: #252B31;
    padding: 46px 20px;
    border-radius: 18px;
    text-align: center;
    color: #C9D1D9;
}

/* Label abu kecil */
.sub-label {
    font-size: 13px;
    color: #9CA3AF;
}

/* Judul di dalam card (biru seperti Figma) */
.card-title {
    font-size: 15px;
    color: #2587E2;
    font-weight: 600;
    margin-bottom: 8px;
}

/* CONTROL BAR: Predict + Auto update */
.control-row {
    margin-top: 8px;
    margin-bottom: 10px;
}

/* Tombol Predict ala Figma */
.predict-btn div.stButton > button {
    background-color: #2587E2;
    color: #FFFFFF;
    border-radius: 999px;
    padding: 10px 32px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: 0.25s;
}
.predict-btn div.stButton > button:hover {
    background-color: #2f8ef0;
}

/* Checkbox Auto update dibuat seperti pill abu */
div.auto-checkbox div[data-testid="stCheckbox"] > label {
    background-color: #252B31;
    border-radius: 999px;
    padding: 8px 16px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    border: 1px solid #374151;
}
div.auto-checkbox div[data-testid="stCheckbox"] label p {
    margin-bottom: 0px;
}
div.auto-checkbox div[data-testid="stCheckbox"] svg {
    width: 14px;
    height: 14px;
}

/* Caption checkbox */
div[data-testid="stCheckbox"] label {
    color: #FFFFFF;
    font-size: 14px;
}

/* HORIZON CHIP (radio) */
.horizon-row {
    margin-top: 2px;
    margin-bottom: 2px;
}

/* styling radio horizon */
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] {
    display: flex !important;
    gap: 10px;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label {
    padding: 6px 18px;
    border-radius: 999px;
    font-size: 14px;
    background-color: #252B31;
    border: 1px solid #374151;
    color: #D5D7F8;
    cursor: pointer;
    transition: 0.2s;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label:hover {
    background-color: #1F2933;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label:has(input[type="radio"]:checked) {
    background-color: #2587E2 !important;
    border-color: #2587E2 !important;
    color: #FFFFFF !important;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] input[type="radio"] {
    opacity: 0;
    position: absolute;
    pointer-events: none;
}

/* Download button biru ala Figma */
div[data-testid="stDownloadButton"] > button {
    background-color: #2587E2;
    color: #FFFFFF;
    border-radius: 999px;
    border: none;
    padding: 8px 24px;
    font-size: 14px;
    font-weight: 500;
}
div[data-testid="stDownloadButton"] > button:disabled {
    background-color: #1f2937;
    color: #9CA3AF;
}

/* Judul chart */
.chart-title {
    font-size: 14px;
    font-weight: 500;
    color: #E5E7EB;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# =============== HALAMAN FORECASTING ===============
def render_forecasting_page() -> None:
    # inisialisasi state
    if "forecast_data" not in st.session_state:
        st.session_state["forecast_data"] = None

    if "forecast_horizon_days" not in st.session_state:
        st.session_state["forecast_horizon_days"] = 7  # default 7D

    # horizon terakhir yang dipakai untuk load data
    if "forecast_last_horizon" not in st.session_state:
        st.session_state["forecast_last_horizon"] = None

    if "forecast_has_run" not in st.session_state:
        st.session_state["forecast_has_run"] = False

    current_horizon = st.session_state["forecast_horizon_days"]

    # ================== WRAP DI MAIN CARD ==================
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # ================= HEADER =================
    top_left, top_right = st.columns([3, 2])

    with top_left:
        # Title dan sub title
        st.markdown(
            """
            <h1 style="
                color:#2587E2;
                font-size:32px;
                font-weight:700;
                margin:0 0 4px 0;">
                Forecasting BBRI
            </h1>
            <p style="
                color:#FFFFFF;
                font-size:16px;
                font-weight:300;
                margin-bottom:16px;">
                Future Price Projection Powered by AI
            </p>
            """,
            unsafe_allow_html=True,
        )

        # Bar: Predict + Auto update
        st.markdown('<div class="control-row">', unsafe_allow_html=True)
        c_predict, c_auto = st.columns([0.7, 1.2])

        predict_clicked = False
        with c_predict:
            st.markdown('<div class="predict-btn">', unsafe_allow_html=True)
            if st.button("Predict", key="forecast_predict"):
                predict_clicked = True
            st.markdown("</div>", unsafe_allow_html=True)

        with c_auto:
            st.markdown('<div class="auto-checkbox">', unsafe_allow_html=True)
            st.checkbox("Auto-update", value=False, key="forecast_auto_update")
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Horizon chips
        st.markdown('<div class="horizon-row">', unsafe_allow_html=True)
        h_label_col, h_radio_col = st.columns([0.32, 1.8])

        with h_label_col:
            st.markdown(
                '<p style="color:#E5E7EB;font-size:14px;margin-top:5px;">Horizon:</p>',
                unsafe_allow_html=True,
            )

        with h_radio_col:
            label_map = {7: "7D", 14: "14D", 30: "30D"}
            reverse_map = {"7D": 7, "14D": 14, "30D": 30}
            current_label = label_map.get(current_horizon, "7D")

            selected_label = st.radio(
                "forecast-horizon",
                ["7D", "14D", "30D"],
                index=["7D", "14D", "30D"].index(current_label),
                horizontal=True,
                label_visibility="collapsed",
            )
            st.session_state["forecast_horizon_days"] = reverse_map[selected_label]
            current_horizon = reverse_map[selected_label]
        st.markdown("</div>", unsafe_allow_html=True)

    # sisi kanan header: last updated & model
    if st.session_state["forecast_data"] is not None:
        last_updated = st.session_state["forecast_data"]["last_updated"]
        best_model = st.session_state["forecast_data"]["model_name"]
    else:
        last_updated = "- (no data yet)"
        best_model = "LightGBM"

    with top_right:
        st.markdown(
            f"""
            <div style="text-align:right;margin-top:6px;">
                <p class="sub-label" style="margin:0 0 4px 0;">
                    Last updated : {last_updated}
                </p>
                <p class="sub-label" style="margin:0 0 30px 0;">
                    Model Used : {best_model}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ================= KAPAN RUN_FORECAST DIPANGGIL =================

    # 1) user klik Predict
    if predict_clicked:
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon
        st.session_state["forecast_has_run"] = True

    # 2) sudah pernah klik Predict lalu ganti horizon
    elif (
        st.session_state["forecast_has_run"]
        and st.session_state["forecast_last_horizon"] != current_horizon
    ):
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon

    # 3) tidak ada perubahan
    else:
        data = st.session_state["forecast_data"]

    # ================== AMBIL DATA DARI STATE ==================
    data = st.session_state["forecast_data"]

    # EMPTY STATE
    if (
        data is None
        or data["forecast_df"] is None
        or len(data["forecast_df"]) == 0
    ):
        st.markdown('<div class="empty-card-wrapper">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="empty-card">
                <h3 style="font-size:20px;font-weight:600;margin-bottom:6px;
                           font-family:'Inter', sans-serif; color:#FFFFFF;">
                    No forecast generated yet
                </h3>
                <p style="font-size:13px;color:#9CA3AF; margin:0;">
                    Click "Predict" to run the model and see the results.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)  # tutup main-card
        return

    # ========== KALAU ADA DATA ==========
    forecast_df: pd.DataFrame = data["forecast_df"]
    today_overview: dict = data["today_overview"]
    forecast_summary: dict = data["forecast_summary"]
    model_eval: dict = data["model_eval"]
    price_fig = data["price_fig"]

    # update horizon dari hasil model
    current_horizon = forecast_summary.get("horizon_days", 7)
    st.session_state["forecast_horizon_days"] = current_horizon

    # ================== METRIC ROW ==================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Today Overview</p>
                <p style="font-size:13px;color:#E5E7EB;margin:0;">Last Close</p>
                <p style="font-size:20px;font-weight:700;margin:0;">
                    {today_overview.get("last_close", "-")}
                </p>
                <p style="font-size:12px;color:#9CA3AF;margin:2px 0 0 0;">
                    Change: {today_overview.get("change_pct","-")}%
                </p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    Volume: {today_overview.get("volume","-")}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Forecast Summary</p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    Horizon: {forecast_summary.get("horizon_days","-")} Days
                </p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    End Price: {forecast_summary.get("end_price","-")}
                </p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    Avg Daily Change: {forecast_summary.get("avg_daily_change","-")}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Model Evaluation</p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    RMSE: {model_eval.get("rmse","-")}
                </p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    MAE: {model_eval.get("mae","-")}
                </p>
                <p style="font-size:12px;color:#9CA3AF;margin:0;">
                    MAPE: {model_eval.get("mape","-")}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # ================== CHART + TABLE ==================
    left, right = st.columns([1.35, 1])

    with left:
        st.markdown(
            """
            <div class="bottom-card">
                <p class="chart-title">Historical vs Forecasted Price</p>
            """,
            unsafe_allow_html=True,
        )

        if price_fig is not None:
            st.plotly_chart(
                price_fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )
        else:
            st.write("Chart goes here")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="bottom-card">
                <p class="chart-title">Forecast Table</p>
            """,
            unsafe_allow_html=True,
        )

        df_show = forecast_df[["date", "forecasted", "lower_bound", "upper_bound"]].copy()
        df_show.columns = ["Date", "Forecasted", "Lower Bound", "Upper Bound"]

        st.dataframe(df_show, use_container_width=True, height=240)

        csv_bytes = df_show.to_csv(index=False).encode("utf-8")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Plot",
                b"",
                file_name="plot.png",
                disabled=True,
            )
        with col2:
            st.download_button(
                "Download CSV",
                csv_bytes,
                file_name="forecast_bbri.csv",
                mime="text/csv",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # tutup .main-card
