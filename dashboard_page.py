import streamlit as st

def render_dashboard(data_dict):

    st.markdown(
        """
        <h1 style="
            color:#2587E2;
            font-size:46px;
            font-weight:700;
        ">
            Indonesian Stock Insights
        </h1>
        <p style="
            color:#FFFFFF;
            font-size:24px;
            font-weight:300;
            margin-bottom:20px;
        ">
            AI-Driven Stock Forecasting Platform
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="big-card">
            <h3 style="color:#2587E2; font-size:37px; font-weight:700; margin:0 0 0 20px;">
                About BBRI-AI
            </h3>
            <p style="font-size:26px; color:#C9D1D9; line-height:1.4; margin:10px; font-weight:400; ">
                BBRI-AI is an intelligent analytics platform designed to provide deep insights into
                Indonesian stocks, with a special focus on BBRI. By combining real-time market data
                with advanced AI forecasting models, BBRI-AI helps investors understand price movements,
                short-term trends, and potential future scenarios. The platform offers interactive
                visualizations, technical indicators, and model evaluation metrics so users can monitor
                performance, compare forecasting horizons, and make data-driven investment decisions
                with greater confidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown(
            """
            <div class="metric-card">
                <h4 style="color:#2587E2; font-size:37px; font-weight:700; margin:0 0 0 20px;">
                    Key Features
                </h4>
                <ul style="font-size:26px; color:#C9D1D9; line-height:1.5; margin:0; padding-left:18px; font-weight:400;">
                    <li>Price predictions for 7, 14, and 30 days</li>
                    <li>Real-time market data from Yahoo Finance</li>
                    <li>Interactive historical &amp; forecasting charts</li>
                    <li>Confidence interval visualization</li>
                    <li>Daily auto-update data</li>
                    <li>Downloadable plots &amp; datasets</li>
                    <li>Best Model : Light GBM</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown(
            """
            <div class="metric-card">
                <h4 style="color:#2587E2; font-size:37px; font-weight:700; margin:0 0 0 20px;">
                    Technology Used
                </h4>
                <ul style="font-size:25px; color:#C9D1D9; line-height:1.5; margin:0; padding-left:18px;">
                   Python, Streamlit, Pandas & NumPy, Plotly visualizations, Yahoo Finance API, Machine Learning model
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="metric-card">
                <h4 style="color:#2587E2; font-size:37px; font-weight:700; margin:0 0 0 20px;">
                    Team Members
                </h4>
                <ul style="font-size:27px; color:#C9D1D9; line-height:1.5; margin:0; padding-left:18px;">
                    <li>A'iza Karimatul Lailiyah</li>
                    <li>Anggi Rahmadillah</li>
                    <li>Geoffrey Jedidiah. S</li>
                    <li>Riche Chalimul Habibah</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
