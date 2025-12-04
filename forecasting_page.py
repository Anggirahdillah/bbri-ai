import streamlit as st
import pandas as pd
from forecasting_engine import run_forecast


def render_forecasting_page() -> None:
    # ========== INIT SESSION STATE ==========
    if "forecast_data" not in st.session_state:
        st.session_state["forecast_data"] = None

    if "forecast_horizon_days" not in st.session_state:
        st.session_state["forecast_horizon_days"] = 7  # default 7D

    if "forecast_last_horizon" not in st.session_state:
        st.session_state["forecast_last_horizon"] = None

    if "forecast_has_run" not in st.session_state:
        st.session_state["forecast_has_run"] = False

    # True = sedang lihat hasil forecast, False = state awal (no forecast)
    if "forecast_show_results" not in st.session_state:
        st.session_state["forecast_show_results"] = False

    current_horizon = st.session_state["forecast_horizon_days"]

    # ================== WRAP DI MAIN CARD ==================
    st.markdown('<div class="main-card">', unsafe_allow_html=True)

    # ================= HEADER =================
    top_left, top_right = st.columns([3, 2])

    # ------------ KIRI: TITLE, BUTTON, HORIZON ------------
    with top_left:
        # Title dan sub title
        st.markdown(
            """
            <h1 style="
                color:#2587E2;
                font-size:46px;
                font-weight:700;
                margin:0 0 4px 0;
            ">
                Forecasting BBRI
            </h1>
            <p style="
                color:#FFFFFF;
                font-size:24px;
                font-weight:300;
                margin-bottom:20px;
            ">
                Future Price Projection Powered by AI
            </p>
            """,
            unsafe_allow_html=True,
        )

        # Bar: Predict / Kembali + Auto update
       # Bar: Predict / Kembali + Auto update
        st.markdown('<div class="control-row forecast-controls">', unsafe_allow_html=True)

        c_predict, c_auto = st.columns([0.5, 0.5])

        predict_clicked = False
        back_clicked = False

        # Pilih CSS class sesuai mode: awal = predict-btn, setelah forecast = back-btn
        btn_wrapper_class = (
            "back-btn" if st.session_state["forecast_show_results"] else "predict-btn"
        )

        # tombol Predict / Kembali
        with c_predict:
            st.markdown(f'<div class="{btn_wrapper_class}">', unsafe_allow_html=True)

            if st.session_state["forecast_show_results"]:
                # SESUDAH PREDICT: tampilkan tombol Kembali
                if st.button("Kembali", key="forecast_back"):
                    back_clicked = True
            else:
                # SEBELUM PREDICT: tampilkan tombol Predict
                if st.button("Predict", key="forecast_predict"):
                    predict_clicked = True

            st.markdown("</div>", unsafe_allow_html=True)

        # checkbox Auto-update (UI aja, belum dipakai)
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
                '<p style="color:#D5D7F8;font-size:20px;margin-bottom:5px;">Horizon:</p>',
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
                key="forecast_horizon_radio",
                horizontal=True,
                label_visibility="collapsed",
            )

            current_horizon = reverse_map[selected_label]
            st.session_state["forecast_horizon_days"] = current_horizon

        st.markdown("</div>", unsafe_allow_html=True)

    # ------------ KANAN: LAST UPDATED & MODEL ------------
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
                <p class="sub-label" style="margin: 0 0 50px 0;">
                    Model Used : {best_model}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ================= KAPAN RUN_FORECAST DIPANGGIL / RESET =================

    # 0) user klik Kembali -> reset ke awal
    if back_clicked:
        st.session_state["forecast_data"] = None
        st.session_state["forecast_last_horizon"] = None
        st.session_state["forecast_has_run"] = False
        st.session_state["forecast_show_results"] = False
        st.session_state["forecast_horizon_days"] = 7

        # langsung rerun supaya tombol berubah jadi "Predict"
        st.rerun()

    # 1) user klik Predict (pertama kali atau setelah kembali)
    elif predict_clicked:
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon
        st.session_state["forecast_has_run"] = True
        st.session_state["forecast_show_results"] = True

        # langsung rerun supaya tombol berubah jadi "Kembali" dan isi forecast muncul
        st.rerun()

    # 2) sudah pernah klik Predict lalu ganti horizon -> auto re-run
    elif (
        st.session_state["forecast_has_run"]
        and st.session_state["forecast_last_horizon"] != current_horizon
    ):
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon
        st.session_state["forecast_show_results"] = True
    else:
        data = st.session_state["forecast_data"]

    # ================== AMBIL DATA DARI STATE ==================
    data = st.session_state["forecast_data"]

    # ================== EMPTY STATE (NO FORECAST) ==================
    if (
        data is None
        or data.get("forecast_df") is None
        or len(data.get("forecast_df")) == 0
    ):
        st.markdown('<div class="empty-card-wrapper">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="empty-card">
                <h3 style="font-size:28px;font-weight:700;
                           font-family:'Inter', sans-serif; color:#FFFFFF;">
                    No forecast generated yet
                </h3>
                <p style="font-size:21px; font-weight:400;color:#818181; margin:0;">
                    Click "Predict" to run the model and see the results.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)  # tutup .main-card
        return

    # ========== KALAU ADA DATA ==========
    forecast_df: pd.DataFrame = data["forecast_df"]
    today_overview: dict = data["today_overview"]
    forecast_summary: dict = data["forecast_summary"]
    model_eval: dict = data["model_eval"]
    price_fig = data["price_fig"]

    # siapkan bytes untuk download plot
    plot_bytes = None
    if price_fig is not None:
        try:
            plot_bytes = price_fig.to_image(format="png")  # butuh kaleido
        except Exception:
            plot_bytes = None

    # update horizon dari hasil model (kalau di dalam data)
    current_horizon = forecast_summary.get("horizon_days", current_horizon)
    st.session_state["forecast_horizon_days"] = current_horizon

    # ================== METRIC ROW ==================
    c1, c2, c3 = st.columns(3)

    # ---------- Today Overview ----------
    last_close = today_overview.get("last_close", "-")
    change_val = today_overview.get("change_pct", "-")
    volume = today_overview.get("volume", "-")

    if isinstance(change_val, (int, float)):
        change_str = f"{change_val:.2f}%"
        change_color = "#00CD34" if change_val >= 0 else "#FF0B0B"
    else:
        change_str = str(change_val)
        change_color = "#F5F5F5"

    with c1:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Today Overview</p>
                <p class="metric-row">
                    <span class="metric-label">Last Close</span>
                    <span class="metric-value">{last_close}</span>
                </p>
                <p class="metric-row">
                    <span class="metric-label">Change</span>
                    <span class="metric-value" style="color:{change_color};">
                        {change_str}
                    </span>
                </p>
                <p class="metric-row">
                    <span class="metric-label">Volume</span>
                    <span class="metric-value">{volume}</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------- Forecast Summary ----------
    horizon_days = forecast_summary.get("horizon_days", "-")
    end_price = forecast_summary.get("end_price", "-")
    avg_val = forecast_summary.get("avg_daily_change", "-")

    if isinstance(avg_val, (int, float)):
        avg_str = f"{avg_val:.2f}%"
        avg_color = "#00CD34" if avg_val >= 0 else "#FF0B0B"
    else:
        avg_str = str(avg_val)
        avg_color = "#F5F5F5"

    with c2:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Forecast Summary</p>
                <p class="metric-row">
                    <span class="metric-label">Horizon</span>
                    <span class="metric-value">{horizon_days} Days</span>
                </p>
                <p class="metric-row">
                    <span class="metric-label">End Price</span>
                    <span class="metric-value">{end_price}</span>
                </p>
                <p class="metric-row">
                    <span class="metric-label">Avg Daily Change</span>
                    <span class="metric-value" style="color:{avg_color};">
                        {avg_str}
                    </span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---------- Model Evaluation ----------
    rmse = model_eval.get("rmse", "-")
    mae = model_eval.get("mae", "-")
    mape = model_eval.get("mape", "-")

    with c3:
        st.markdown(
            f"""
            <div class="small-card">
                <p class="card-title">Model Evaluation</p>
                <p class="metric-row">
                    <span class="metric-label">RMSE</span>
                    <span class="metric-value">{rmse}</span>
                </p>
                <p class="metric-row">
                    <span class="metric-label">MAE</span>
                    <span class="metric-value">{mae}</span>
                </p>
                <p class="metric-row">
                    <span class="metric-label">MAPE</span>
                    <span class="metric-value">{mape}%</span>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # ================== CHART + TABLE ==================
    left, right = st.columns([1.35, 1])

    # ---------- CHART ----------
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

    # ---------- TABLE + DOWNLOAD ----------
    with right:
        st.markdown(
            """
            <div class="bottom-card">
                <p class="chart-title">Forecast Table</p>
            """,
            unsafe_allow_html=True,
        )

        df_show = forecast_df[
            ["date", "forecasted", "lower_bound", "upper_bound"]
        ].copy()
        df_show.columns = ["Date", "Forecasted", "Lower Bound", "Upper Bound"]

        st.dataframe(df_show, use_container_width=True, height=240)

        csv_bytes = df_show.to_csv(index=False).encode("utf-8")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Plot",
                data=plot_bytes if plot_bytes is not None else b"",
                file_name="forecast_bbri_plot.png",
                mime="image/png",
                disabled=(plot_bytes is None),
            )
        with col2:
            st.download_button(
                "Download CSV",
                data=csv_bytes,
                file_name="forecast_bbri.csv",
                mime="text/csv",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # tutup .main-card
