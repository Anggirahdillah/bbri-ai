import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pickle


# ======================= ENGINE UTAMA =======================

def run_forecast(ticker: str = "BBRI.JK", horizon_days: int = 7) -> dict:
    """
    Engine forecast sederhana untuk BBRI.

    - Historical: data/data_saham_bbri_jk*.csv
    - Evaluasi model: data/model_evaluation_result.csv
    - (opsional) Meta model: models/best_model_meta.pkl
    - Forecast: naive + drift dari data historis (bisa diganti dengan model asli)
    """

    # ========== 1. LOAD HISTORICAL ========== #
    # cari file yang namanya diawali 'data_saham_bbri_jk'
    hist_path = None
    data_dir = "data"
    if os.path.isdir(data_dir):
        for fname in os.listdir(data_dir):
            if fname.lower().startswith("data_saham_bbri_jk"):
                hist_path = os.path.join(data_dir, fname)
                break

    if hist_path is None or not os.path.exists(hist_path):
        # fallback: kalau ga ketemu, balikin kosong
        empty_df = pd.DataFrame(columns=["date", "forecasted", "lower_bound", "upper_bound"])
        return {
            "forecast_df": empty_df,
            "today_overview": {},
            "forecast_summary": {},
            "model_eval": {},
            "price_fig": None,
            "last_updated": "-",
            "model_name": "LightGBM",
        }

    hist = pd.read_csv(hist_path)

    # Normalisasi nama kolom
    # asumsikan ada kolom tanggal & close, adjust kalau beda
    cols_lower = [c.lower() for c in hist.columns]
    col_date = hist.columns[cols_lower.index("date")] if "date" in cols_lower else hist.columns[0]
    # coba cari 'close' / 'close_price'
    if "close" in cols_lower:
        col_close = hist.columns[cols_lower.index("close")]
    elif "close_price" in cols_lower:
        col_close = hist.columns[cols_lower.index("close_price")]
    else:
        # kalau ga ada, pakai kolom terakhir sebagai harga
        col_close = hist.columns[-1]

    hist[col_date] = pd.to_datetime(hist[col_date])
    hist = hist.sort_values(col_date)

    # ========== 2. TODAY OVERVIEW ========== #
    last_row = hist.iloc[-1]
    last_close = float(last_row[col_close])

    if len(hist) > 1:
        prev_close = float(hist[col_close].iloc[-2])
    else:
        prev_close = last_close

    change_pct = (last_close - prev_close) / prev_close * 100 if prev_close != 0 else 0.0

    # volume kalau ada
    if "volume" in cols_lower:
        col_vol = hist.columns[cols_lower.index("volume")]
        volume_val = float(last_row[col_vol])
        volume_str = f"{volume_val:,.0f}"
    else:
        volume_str = "-"

    today_overview = {
        "last_close": round(last_close, 2),
        "change_pct": round(change_pct, 2),
        "volume": volume_str,
    }

    # ========== 3. FORECAST (NAIVE + DRIFT) ========== #
    # Pakai rata-rata return 20 hari terakhir sebagai drift
    close_series = hist[col_close].astype(float)
    returns = close_series.pct_change().dropna()

    if len(returns) >= 5:
        drift = returns.tail(20).mean()
        vol = returns.tail(20).std()
    else:
        drift = 0.0
        vol = 0.0

    start_date = hist[col_date].iloc[-1]

    future_dates = [start_date + timedelta(days=i) for i in range(1, horizon_days + 1)]
    forecast_prices = []
    lower_bounds = []
    upper_bounds = []

    current_price = last_close
    for i in range(1, horizon_days + 1):
        current_price = current_price * (1 + drift)
        forecast_prices.append(current_price)

        band = current_price * vol * np.sqrt(i) if vol > 0 else current_price * 0.02
        lower_bounds.append(current_price - band)
        upper_bounds.append(current_price + band)

    forecast_df = pd.DataFrame(
        {
            "date": future_dates,
            "forecasted": forecast_prices,
            "lower_bound": lower_bounds,
            "upper_bound": upper_bounds,
        }
    )

    # ========== 4. FORECAST SUMMARY ========== #
    end_price = float(forecast_df["forecasted"].iloc[-1])
    avg_daily_change = drift * 100 if drift is not None else 0.0

    forecast_summary = {
        "horizon_days": int(horizon_days),
        "end_price": round(end_price, 2),
        "avg_daily_change": round(avg_daily_change, 2),
    }

    # ========== 5. MODEL EVALUATION DARI FILE ========== #
    # misal: data/model_evaluation_result.csv
    metrics_path = os.path.join("data", "model_evaluation_result.csv")
    model_eval = {"rmse": 0.0, "mae": 0.0, "mape": 0.0}
    model_name = "LightGBM"

    if os.path.exists(metrics_path):
        try:
            metrics_df = pd.read_csv(metrics_path)
            # ambil baris pertama
            row0 = metrics_df.iloc[0]
            # sesuaikan nama kolom kalau beda
            cols = [c.lower() for c in metrics_df.columns]
            rmse_col = metrics_df.columns[cols.index("rmse")] if "rmse" in cols else None
            mae_col = metrics_df.columns[cols.index("mae")] if "mae" in cols else None
            mape_col = metrics_df.columns[cols.index("mape")] if "mape" in cols else None

            if rmse_col:
                model_eval["rmse"] = float(row0[rmse_col])
            if mae_col:
                model_eval["mae"] = float(row0[mae_col])
            if mape_col:
                model_eval["mape"] = float(row0[mape_col])
        except Exception:
            pass

    # coba ambil nama model dari models/best_model_meta.pkl
    meta_path = os.path.join("models", "best_model_meta.pkl")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "rb") as f:
                meta = pickle.load(f)
            if isinstance(meta, dict) and "model_name" in meta:
                model_name = meta["model_name"]
        except Exception:
            pass

    # ========== 6. FIGURE PLOTLY: HIST VS FORECAST ========== #
    fig = go.Figure()

    # ambil 60 hari terakhir
    hist_tail = hist.tail(60)
    fig.add_trace(
        go.Scatter(
            x=hist_tail[col_date],
            y=hist_tail[col_close],
            mode="lines",
            name="Historical Close",
            line=dict(color="#22C55E", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=forecast_df["date"],
            y=forecast_df["forecasted"],
            mode="lines",
            name="Forecast",
            line=dict(color="#3B82F6", width=2, dash="dash"),
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=5, r=5, t=10, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#9CA3AF", size=12),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#6B7280"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            zeroline=False,
            tickfont=dict(color="#6B7280"),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    # ========== 7. RETURN ========== #
    return {
        "forecast_df": forecast_df,
        "today_overview": today_overview,
        "forecast_summary": forecast_summary,
        "model_eval": model_eval,
        "price_fig": fig,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "model_name": model_name,
    }
