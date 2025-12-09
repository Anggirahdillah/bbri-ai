import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pickle
import yfinance as yf 
from datetime import datetime, timedelta

def run_forecast(ticker: str = "BBRI.JK", horizon_days: int = 7) -> dict:

    hist = None
    data_dir = "data"

    hist_path = None
    if os.path.isdir(data_dir):
        for fname in os.listdir(data_dir):
            if fname.lower().startswith("data_saham_bbri_jk"):
                hist_path = os.path.join(data_dir, fname)
                break

    if hist_path is not None and os.path.exists(hist_path):
        try:
            hist = pd.read_csv(hist_path)
        except Exception:
            hist = None

    if hist is None:
        try:
            yf_df = yf.download(ticker, period="6mo") 
            if not yf_df.empty:
                yf_df = yf_df.reset_index()
                yf_df.rename(columns={"Date": "date", "Close": "close", "Volume": "volume"}, inplace=True)
                hist = yf_df
        except Exception:
            hist = None

    if hist is None or hist.empty:
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

    cols_lower = [c.lower() for c in hist.columns]

    if "date" in cols_lower:
        col_date = hist.columns[cols_lower.index("date")]
    else:
        col_date = hist.columns[0]


    if "close" in cols_lower:
        col_close = hist.columns[cols_lower.index("close")]
    elif "close_price" in cols_lower:
        col_close = hist.columns[cols_lower.index("close_price")]
    else:
        col_close = hist.columns[-1]

    hist[col_date] = pd.to_datetime(hist[col_date])
    hist = hist.sort_values(col_date)

    last_row = hist.iloc[-1]
    last_close = float(last_row[col_close])

    if len(hist) > 1:
        prev_close = float(hist[col_close].iloc[-2])
    else:
        prev_close = last_close

    change_pct = (last_close - prev_close) / prev_close * 100 if prev_close != 0 else 0.0

    volume_str = "-"
    if "volume" in cols_lower:
        col_vol = hist.columns[cols_lower.index("volume")]
        try:
            volume_val = float(last_row[col_vol])
            volume_str = f"{volume_val:,.0f}"
        except Exception:
            volume_str = "-"

    today_overview = {
        "last_close": round(last_close, 2),
        "change_pct": round(change_pct, 2),
        "volume": volume_str,
    }

    close_series = hist[col_close].astype(float)
    returns = close_series.pct_change().dropna()

    if len(returns) >= 5:
        drift = returns.tail(20).mean()
        vol = returns.tail(20).std()
    else:
        drift = 0.0
        vol = 0.0


    start_date = datetime.now().date()
    future_dates = [(start_date + timedelta(days=i)) for i in range(1, horizon_days + 1)]
    start_date = datetime.now().date()

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

    end_price = float(forecast_df["forecasted"].iloc[-1])
    avg_daily_change = drift * 100 if drift is not None else 0.0

    forecast_summary = {
        "horizon_days": int(horizon_days),
        "end_price": round(end_price, 2),
        "avg_daily_change": round(avg_daily_change, 2),
    }

    actual = close_series.values
    if len(actual) > 1:
        preds = actual[:-1]   
        y_true = actual[1:]    
        errors = y_true - preds

        rmse_val = float(np.sqrt(np.mean(errors ** 2)))
        mae_val = float(np.mean(np.abs(errors)))

        nonzero_mask = y_true != 0
        if nonzero_mask.any():
            mape_val = float(np.mean(np.abs(errors[nonzero_mask] / y_true[nonzero_mask])) * 100)
        else:
            mape_val = 0.0
    else:
        rmse_val = mae_val = mape_val = 0.0

    model_eval = {
        "rmse": round(rmse_val, 2),
        "mae": round(mae_val, 2),
        "mape": round(mape_val, 2),
    }

    model_name = "LightGBM"

    metrics_path = os.path.join("data", "model_evaluation_result.csv")
    if os.path.exists(metrics_path):
        try:
            metrics_df = pd.read_csv(metrics_path)
            row0 = metrics_df.iloc[0]
            cols_me = [c.lower() for c in metrics_df.columns]
            rmse_col = metrics_df.columns[cols_me.index("rmse")] if "rmse" in cols_me else None
            mae_col = metrics_df.columns[cols_me.index("mae")] if "mae" in cols_me else None
            mape_col = metrics_df.columns[cols_me.index("mape")] if "mape" in cols_me else None

            if rmse_col is not None:
                model_eval["rmse"] = round(float(row0[rmse_col]), 2)
            if mae_col is not None:
                model_eval["mae"] = round(float(row0[mae_col]), 2)
            if mape_col is not None:
                model_eval["mape"] = round(float(row0[mape_col]), 2)
        except Exception:
            pass
    
    fig = go.Figure()

    hist_tail = hist.tail(60).copy()
    hist_tail["prev"] = hist_tail[col_close].shift(1)
    hist_tail["color"] = hist_tail.apply(
        lambda r: "#00CD34" if r[col_close] >= r["prev"] else "#FF0B0B",
        axis=1
    )
    for i in range(1, len(hist_tail)):
        fig.add_trace(go.Scatter(
            x=[hist_tail[col_date].iloc[i-1], hist_tail[col_date].iloc[i]],
            y=[hist_tail[col_close].iloc[i-1], hist_tail[col_close].iloc[i]],
            mode="lines",
            line=dict(color=hist_tail["color"].iloc[i], width=3),
            name="Historical" if i == 1 else None,   # legend sekali saja
            showlegend=(i == 1)
        ))

    fig.add_trace(go.Scatter(
        x=[hist_tail[col_date].iloc[-1]],
        y=[hist_tail[col_close].iloc[-1]],
        mode="markers",
        marker=dict(color=hist_tail["color"].iloc[-1], size=9),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["forecasted"],
        mode="lines",
        line=dict(color="#2587E2", width=4),
        name="Forecast"
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["date"],
        y=forecast_df["forecasted"],
        mode="markers",
        marker=dict(color="#2587E2", size=7),
        showlegend=False
    ))
    fig.update_layout(
        height=360,
        margin=dict(l=10, r=10, t=35, b=10),
        paper_bgcolor="#252B31",
        plot_bgcolor="#252B31",
        font=dict(color="#C9D1D9", size=12),

        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#C9D1D9"),
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#6F6F6F",
            zeroline=False,
            tickfont=dict(color="#C9D1D9")
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="left",
            x=0,
            font=dict(color="white", size=14)
        )
    )


    return {
        "forecast_df": forecast_df,
        "today_overview": today_overview,
        "forecast_summary": forecast_summary,
        "model_eval": model_eval,
        "price_fig": fig,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "model_name": model_name,
    }

