from typing import Optional

import streamlit as st
import pandas as pd

from forecasting_engine import run_forecast  # pastikan file ini ada ya


# =============== CSS KHUSUS HALAMAN FORECASTING ===============
st.markdown("""
<style>
.main-card {
    background-color: #111827;
    padding: 25px 30px;
    border-radius: 24px;
}

/* Kartu kecil (Today Overview, Forecast Summary, Model Eval) */
.small-card {
    background-color: #252B31;
    padding: 18px 20px;
    border-radius: 14px;
}

/* Kartu besar bawah (chart + tabel) */
.bottom-card {
    background-color: #252B31;
    padding: 18px 20px;
    border-radius: 14px;
    height: 100%;
}

/* Empty state */
.empty-card {
    background-color: #252B31;
    padding: 40px 20px;
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
    font-size: 16px;
    color: #2587E2;
    font-weight: 600;
    margin-bottom: 6px;
}

/* Chips Horizon di header (7D 14D 30D) */
.horizon-chip {
    background-color: #252B31;
    color: #D5D7F8;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 14px;
    border: 1px solid #374151;
    margin-right: 4px;
}
.horizon-chip.active {
    background-color: #2587E2;
    border-color: #2587E2;
    color:white;
}

/* Tombol Predict */
div.stButton > button {
    background-color: #2587E2;
    color: white;
    border-radius: 18px;
    padding: 10px 32px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: 0.25s;
}
div.stButton > button:hover {
    background-color: #2f8ef0;
}

/* Checkbox Auto-update */
div[data-testid="stCheckbox"] label {
    color: #FFFFFF;
    font-size: 15px;
}

/* Radio horizon di bawah chart (kalau dipakai nanti) */
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] {
    display: flex !important;
    gap: 10px;
    justify-content: center;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label {
    padding: 6px 16px;
    border-radius: 999px;
    font-size: 14px;
    background-color: #111827;
    border: 1px solid #374151;
    color: #E5E7EB;
    cursor: pointer;
    transition: 0.2s;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label:hover {
    background-color: #1F2933;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label:has(input[type="radio"]:checked) {
    background-color: #2587E2 !important;
    border-color: #2587E2 !important;
    color: white !important;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] input[type="radio"] {
    opacity: 0;
    position: absolute;
    pointer-events: none;
}
</style>
""", unsafe_allow_html=True)


# =============== HALAMAN FORECASTING ===============
def render_forecasting_page() -> None:
    """
    Halaman Forecasting BBRI.
    """

    # ---------- INIT STATE ----------
    if "forecast_data" not in st.session_state:
        st.session_state["forecast_data"] = None

    if "forecast_horizon_days" not in st.session_state:
        st.session_state["forecast_horizon_days"] = 7  # default 7D

    if "forecast_last_horizon" not in st.session_state:
        st.session_state["forecast_last_horizon"] = None

    if "forecast_has_run" not in st.session_state:
        st.session_state["forecast_has_run"] = False

    current_horizon = st.session_state["forecast_horizon_days"]

    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # ================= HEADER =================
    top_left, top_right = st.columns([3, 2])

    # ----- kiri: title, tombol, horizon -----
    with top_left:
        st.markdown(
            """
            <h1 style="
                color:#2587E2;
                font-size:46px;
                font-weight:700;
                margin:0 0 8px 0;">
                Forecasting BBRI
            </h1>
            <p style="
                color:#FFFFFF;
                font-size:24px;
                font-weight:300;
                margin-bottom:20px;">
                Future Price Projection Powered by AI
            </p>
            """,
            unsafe_allow_html=True,
        )

        col_btn, col_auto = st.columns([1, 1.4])

        # tombol Predict
        predict_clicked = False
        with col_btn:
            st.markdown('<div class="predict-btn">', unsafe_allow_html=True)
            if st.button("Predict", key="forecast_predict"):
                predict_clicked = True
            st.markdown("</div>", unsafe_allow_html=True)

        # auto-update + horizon radio (chip)
        with col_auto:
            st.checkbox("Auto-update", value=False)

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

    # ----- kanan: last updated + model name -----
    if st.session_state["forecast_data"] is not None:
        last_updated = st.session_state["forecast_data"]["last_updated"]
        best_model = st.session_state["forecast_data"]["model_name"]
    else:
        last_updated = "- (no data yet)"
        best_model = "LightGBM"

    with top_right:
        st.markdown(
            f"""
            <div style="text-align:right;margin-top:12px;">
                <p class="sub-label" style="margin:0 0 4px 0;">
                    Last updated : {last_updated}
                </p>
                <p class="sub-label" style="margin:0;">
                    Model Used : {best_model}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ================= LOGIC PANGGIL run_forecast =================
    data = st.session_state["forecast_data"]

    # 1) User baru klik Predict
    if predict_clicked:
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon
        st.session_state["forecast_has_run"] = True

    # 2) Sudah pernah Predict, tapi horizon berubah (7D -> 14D / 30D)
    elif (
        st.session_state["forecast_has_run"]
        and st.session_state["forecast_last_horizon"] != current_horizon
    ):
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon

    # kalau tidak, pakai data yang sudah ada (data sudah diambil di awal)

    st.write("")

    # ================= EMPTY STATE =================
    if (
        data is None
        or "forecast_df" not in data
        or data["forecast_df"] is None
        or len(data["forecast_df"]) == 0
    ):
        st.markdown(
            """
            <div class="empty-card">
                <h3 style="font-size:28px;font-weight:600;margin-bottom:8px;
                           font-family:'Inter', sans-serif; color:#FFFFFF;">
                    No forecast generated yet
                </h3>
                <p style="font-size:14px;color:#818181; margin:0;">
                    Click "Predict" to run the model and see the results.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # ================= UNPACK DATA =================
    forecast_df: pd.DataFrame = data["forecast_df"]
    today_overview: dict = data["today_overview"]
    forecast_summary: dict = data["forecast_summary"]
    model_eval: dict = data["model_eval"]
    price_fig = data["price_fig"]

    # update horizon state dari hasil summary
    current_horizon = forecast_summary.get("horizon_days", current_horizon)
    st.session_state["forecast_horizon_days"] = current_horizon
    st.session_state["forecast_last_horizon"] = current_horizon

    # ================= 3 METRIC CARDS =================
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Today Overview</p>
                <p style="font-size:14px;color:#E5E7EB;margin:0;">Last Close</p>
                <p style="font-size:20px;font-weight:700;margin:0;">
                    {today_overview.get("last_close", "-")}
                </p>
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
                    Change: {today_overview.get("change_pct","-")}%
                </p>
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
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
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
                    Horizon: {forecast_summary.get("horizon_days","-")} Days
                </p>
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
                    End Price: {forecast_summary.get("end_price","-")}
                </p>
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
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
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
                    RMSE: {model_eval.get("rmse","-")}
                </p>
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
                    MAE: {model_eval.get("mae","-")}
                </p>
                <p style="font-size:13px;color:#9CA3AF;margin:0;">
                    MAPE: {model_eval.get("mape","-")}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # ================= CHART + TABLE =================
    left, right = st.columns([1.3, 1])

    # ----- kiri: chart -----
    with left:
        st.markdown(
            """
            <div class="bottom-card">
                <p class="card-title">Historical vs Forecasted Price</p>
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

    # ----- kanan: table + download -----
    with right:
        st.markdown(
            """
            <div class="bottom-card">
                <p class="card-title">Forecast Table</p>
            """,
            unsafe_allow_html=True,
        )

        # table
        df_show = forecast_df[["date", "forecasted", "lower_bound", "upper_bound"]].copy()
        df_show.columns = ["Date", "Forecasted", "Lower Bound", "Upper Bound"]

        st.dataframe(df_show, use_container_width=True, height=260)

        # CSV bytes
        csv_bytes = df_show.to_csv(index=False).encode("utf-8")

        # PNG bytes dari plot (butuh kaleido terinstall)
        plot_bytes = None
        if price_fig is not None:
            try:
                plot_bytes = price_fig.to_image(
                    format="png",
                    width=1100,
                    height=450,
                    scale=2,
                )
            except Exception:
                plot_bytes = None
                st.warning("Gagal membuat plot PNG. Install dulu: pip install -U kaleido")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download Plot",
                data=plot_bytes if plot_bytes else b"",
                file_name=f"forecast_{current_horizon}d.png",
                mime="image/png",
                disabled=(plot_bytes is None),
            )

        with col2:
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name=f"forecast_bri_{current_horizon}d.csv",
                mime="text/csv",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # tutup main-card
