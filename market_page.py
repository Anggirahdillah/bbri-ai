import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

TICKER_LIST = [
    "BBRI.JK",
    "BBNI.JK",
    "BBCA.JK",
    "BMRI.JK",
    "ASII.JK",
    "TLKM.JK",
    "UNVR.JK",
    "ANTM.JK",
    "PGAS.JK",
    "MEDC.JK",
]

def fetch_price_data(ticker: str, horizon: str) -> pd.DataFrame:
    if horizon == "1D":
        period = "1d"
        interval = "5m"
    elif horizon == "1W":
        period = "5d"
        interval = "30m"
    elif horizon == "1M":
        period = "1mo"
        interval = "1d"
    else:  # "1Y"
        period = "1y"
        interval = "1d"

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )
    return df

def compute_metrics(df: pd.DataFrame, horizon: str):
    last = df.iloc[-1]
    current_price = float(last["Close"])
    open_price = float(last["Open"])
    low_price = float(df["Low"].min())
    high_price = float(df["High"].max())
    volume = float(last["Volume"])

    if len(df) > 1:
        prev_close = float(df["Close"].iloc[-2])
        change_pct = (current_price - prev_close) / prev_close * 100.0
    else:
        change_pct = 0.0
        
    if horizon == "1W" and len(df) >= 6:
        prev_5d_close = float(df["Close"].iloc[-6])
        change_pct = ((current_price - prev_5d_close) / prev_5d_close) * 100.0

    return current_price, open_price, low_price, high_price, volume, change_pct


def format_number(num: float) -> str:
    return f"{num:,.0f}"

def format_volume(vol: float) -> str:
    if vol >= 1_000_000_000:
        return f"{vol / 1_000_000_000:.2f} B"
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.2f} M"
    if vol >= 1_000:
        return f"{vol / 1_000:.2f} K"
    return f"{vol:,.0f}"

def build_price_chart(df, ticker):
    try:
        df = df.copy()
        if not isinstance(df.index, pd.DatetimeIndex):
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
                df = df.set_index("Date")
            elif "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df = df.set_index("date")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]
        price_col = None
        for col in df.columns:
            if "close" in str(col).lower():
                price_col = col
                break
            if "price" in str(col).lower():
                price_col = col
                break
        if price_col is None:
            price_col = df.columns[-1]
        df["Close"] = pd.to_numeric(df[price_col], errors="coerce")
        df = df.dropna(subset=["Close"])
        if len(df) < 2:
            st.error("Data terlalu sedikit / kosong🙏")
            return go.Figure()
        start = df["Close"].iloc[0]
        end = df["Close"].iloc[-1]
        color = "green" if end >= start else "red"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Close"],
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=6),
            name=ticker
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white", size=12),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )
        return fig
    except Exception as e:
        st.error(f"Chart Error FIX FINAL: {e}")
        return go.Figure()
    
def render_market_overview(_data_dict):
    if "market_horizon" not in st.session_state:
        st.session_state.market_horizon = "1D"
    params = st.query_params
    clicked = params.get("h", None)
    if clicked:
        if isinstance(clicked, list):
            clicked = clicked[0]
        if clicked in ["1D", "1W", "1M", "1Y"]:
            st.session_state.market_horizon = clicked
        st.query_params.clear()
    st.markdown('<div class="page-panel">', unsafe_allow_html=True)

    st.markdown(
        """
        <h2 style="
            color:#2587E2;
            font-size:46px;
            font-weight:700;">Market Overview</h2>
        <p style="
            color:#FFFFFF;
            font-size:24px;
            font-weight:300;
            margin-bottom:20px;">
            Real-Time Stock Data &amp; Intraday Movement
        </p>
        """,
        unsafe_allow_html=True,
    )
 
    sp_left, col_label, col_select, sp_right = st.columns([0.1, 0.8, 0.8, 4])
    with col_label:
        st.markdown(
            """
            <p style="
                color:#C9D1D9;
                font-size:22px;
                font-weight:400;
                text-align:right;
                margin-top:6px;
            ">
                Select Ticker :
            </p>
            """,
            unsafe_allow_html=True,
        )
    with col_select:
        ticker = st.selectbox(
            "",
            options=TICKER_LIST,
            index=0,
            key="market_ticker",
            label_visibility="collapsed", 
        )

        
    if "market_horizon" not in st.session_state:
        st.session_state.market_horizon = "1D"
    horizon = st.session_state.market_horizon
    df = fetch_price_data(ticker, horizon)
    if df.empty:
        st.warning("PASAR SEDANG TUTUP. SILAHKAN CHECK DIHARI SELANJUTNYA")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    current_price, open_price, low_price, high_price, volume, change_pct = compute_metrics(df, horizon)
    st.write("")

    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <p style="
                    color:#2587E2;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:33px;">Current Price</p>
                <p style="
                    color:#C9D1D9;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:57px;">{format_number(current_price)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <p style="
                    color:#2587E2;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:33px;">Open</p>
                <p style="
                    color:#C9D1D9;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:57px;">{format_number(open_price)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r1c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <p style="
                    color:#2587E2;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:33px;">Volume</p>
                <p style="
                    color:#C9D1D9;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:57px;">{format_volume(volume)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.write("")

    r2_left, r2_right = st.columns([1, 2])
    with r2_left:
        low_col, high_col = st.columns(2)
        with low_col:
            st.markdown(
                f"""
                <div class="metric-card-low">
                    <p style="
                        color:#2587E2;
                        font-family: Inter, sans-serif;
                        font-weight:500;
                        text-align:center;
                        font-size:33px;">Low</p>
                    <p style="
                        color:#C9D1D9;
                        font-family: Inter, sans-serif;
                        font-weight:500;
                        text-align:center;
                        font-size:57px;">{format_number(low_price)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with high_col:
            st.markdown(
                f"""
                <div class="metric-card-high">
                    <p style="
                        color:#2587E2;
                        font-family: Inter, sans-serif;
                        font-weight:500;
                        text-align:center;
                        font-size:33px;">High</p>
                    <p style="
                        color:#C9D1D9;
                        font-family: Inter, sans-serif;
                        font-weight:500;
                        text-align:center;
                        font-size:57px;">{format_number(high_price)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.write("")

        st.markdown(
            f"""
            <div class="metric-card-change">
                <p style="
                    color:#2587E2;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:33px;">Change %</p>
                <p style="
                    color:#C9D1D9;
                    font-family: Inter, sans-serif;
                    font-weight:500;
                    text-align:center;
                    font-size:57px;">{change_pct:+.2f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2_right:
        with st.container():
            st.markdown(
                """
                <p style="
                    color:#2587E2;
                    font-size:32px;
                    text-align:center;
                    margin-bottom:20px;
                ">
                    Price Trend
                </p>
                """,
                unsafe_allow_html=True,
            )
            price_fig = build_price_chart(df, ticker)
            price_fig.update_layout(
                height=320,
                margin=dict(l=200, r=0, t=10, b=0),
            )
            st.plotly_chart(
                price_fig,
                use_container_width=True,
                config={"displayModeBar": False},
            )

            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            sp_left, c1, c2, c3, c4, sp_right = st.columns([3, 2, 2, 2, 2, 1])
            cols = [c1, c2, c3, c4]
            labels = ["1D", "1W", "1M", "1Y"]
            active = st.session_state.market_horizon
            for label, col in zip(labels, cols):
                with col:
                    if label == active:
                        st.markdown(
                            f"""
                            <div class="h-tab-text h-tab-active">{label}</div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        if st.button(label, key=f"horizon_{label}", help="", type="secondary"):
                            st.session_state.market_horizon = label
                            st.rerun()
    
                        st.markdown(
                            f"""
                            <script>
                            var btn = window.parent.document.querySelector('button[key="horizon_{label}"]');
                            if (btn) {{
                                btn.classList.add('h-tab-btn');
                            }}
                            </script>
                            """,
                            unsafe_allow_html=True,
                        ) 