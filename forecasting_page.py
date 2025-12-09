from typing import Optional
from io import BytesIO
from forecasting_engine import run_forecast
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Stock Forecast Dashboard", layout="wide")

def render_forecasting_page() -> None:
    if "forecast_data" not in st.session_state:
        st.session_state["forecast_data"] = None

    if "forecast_horizon_days" not in st.session_state:
        st.session_state["forecast_horizon_days"] = 7

    if "forecast_last_horizon" not in st.session_state:
        st.session_state["forecast_last_horizon"] = None

    if "forecast_has_run" not in st.session_state:
        st.session_state["forecast_has_run"] = False

    if "forecast_show_results" not in st.session_state:
        st.session_state["forecast_show_results"] = False
    current_horizon = st.session_state["forecast_horizon_days"]


    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    top_left, top_right = st.columns([3, 2])
    with top_left:
        st.markdown(
            """
            <h1 style="
                color:#2587E2;
                font-size:46px;
                font-weight:700;
                margin:0 0 4px 0;
            ">
                Forecasting BBRI.JK
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

    st.markdown('<div class="control-row">', unsafe_allow_html=True)
    c_predict = st.columns(1)[0]
    predict_clicked = False
    back_clicked = False
    with c_predict:
        st.markdown('<div class="predict-btn">', unsafe_allow_html=True)
        if st.session_state["forecast_show_results"]:
            if st.button("Kembali", key="forecast_back"):
                back_clicked = True
        else:
            if st.button("Predict", key="forecast_predict"):
                predict_clicked = True
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="horizon-row">', unsafe_allow_html=True)
    h_label_col, h_radio_col = st.columns([0.22, 1])
    with h_label_col:
     st.markdown(
        '<p style="color:#D5D7F8;font-size:26px;margin-right:0;padding-right:0;text-align:left;">choose horizon:</p>',
        unsafe_allow_html=True,
    )
    with h_radio_col:
        current_horizon = st.session_state["forecast_horizon_days"]
        labels = [("7D", 7), ("14D", 14), ("30D", 30)]
        sp_right, c1, c2, c3, sp_left = st.columns([2, 5, 5, 5, 20])
        cols = [c1, c2, c3]
        for (label, days), col in zip(labels, cols):
            with col:
                if current_horizon == days:
                    st.markdown(
                        f"""
                        <div class="h-tab-text h-tab-active">{label}</div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button(label, key=f"forecast_horizon_btn_{days}", help="", type="secondary"):
                        st.session_state["forecast_horizon_days"] = days
                        st.rerun()
                    st.markdown(
                        f"""
                        <script>
                        var btn = window.parent.document.querySelector('button[key="forecast_horizon_btn_{days}"]');
                        if (btn) {{
                            btn.classList.add('h-tab-text');
                        }}
                        </script>
                        """,
                        unsafe_allow_html=True,
                    )

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

    if back_clicked:
        st.session_state["forecast_data"] = None
        st.session_state["forecast_last_horizon"] = None
        st.session_state["forecast_has_run"] = False
        st.session_state["forecast_show_results"] = False
        st.session_state["forecast_horizon_days"] = 7
        data = None
        st.rerun()
    elif predict_clicked:
        data = run_forecast(ticker="BBRI.JK", horizon_days=current_horizon)
        st.session_state["forecast_data"] = data
        st.session_state["forecast_last_horizon"] = current_horizon
        st.session_state["forecast_has_run"] = True
        st.session_state["forecast_show_results"] = True
        st.rerun()
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

    if (
        data is None
        or data["forecast_df"] is None
        or len(data["forecast_df"]) == 0
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
        st.markdown("</div>", unsafe_allow_html=True)
        return

    forecast_df: pd.DataFrame = data["forecast_df"]
    today_overview: dict = data["today_overview"]
    forecast_summary: dict = data["forecast_summary"]
    model_eval: dict = data["model_eval"]
    price_fig = data["price_fig"]
    plot_bytes = None
    current_horizon = forecast_summary.get("horizon_days", 7)
    st.session_state["forecast_horizon_days"] = current_horizon

    c1, c2, c3 = st.columns(3)

    last_close = today_overview.get("last_close", "-")
    change_val = today_overview.get("change_pct", "-")
    volume = today_overview.get("volume", "-")
    if isinstance(change_val, (int, float, float)):
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

    horizon_days = forecast_summary.get("horizon_days", "-")
    end_price = forecast_summary.get("end_price", "-")
    avg_val = forecast_summary.get("avg_daily_change", "-")
    if isinstance(avg_val, (int, float, float)):
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
        table_html = df_show.to_html(index=False, classes="styled-table")
        st.markdown(table_html, unsafe_allow_html=True)

        csv_bytes = df_show.to_csv(index=False).encode("utf-8")
        col1 = st.columns(4)[0]
        with col1:
            st.download_button(
                "⤓ Download CSV",
                data=csv_bytes,
                file_name="forecast_bbri.csv",
                mime="text/csv",
            )

st.markdown("</div>", unsafe_allow_html=True)
        
