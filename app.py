import streamlit as st
import os
from pathlib import Path
from loaders import load_models, load_preprocessing, load_data
from dashboard_page import render_dashboard
from market_page import render_market_overview
from forecasting_page import render_forecasting_page
from forecasting_engine import run_forecast

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="BBRI-AI",
    page_icon="🅱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
body { background-color: #1A1E23; }
.main { background-color: #1A1E23; }

[data-testid="stAppViewContainer"],
.block-container {
    background-color: #1A1E23 !important;
}

section[data-testid="stSidebar"] {
    background-color: #072A4A;
    padding-top: 10px;
}
            
div[role="radiogroup"] {
    display: block !important;
    padding: 10px;
}

div[role="radiogroup"] > label > div:first-child {
    display: none !important;
}

div[role="radiogroup"] > label {
    display: flex;
    align-items: flex-start;
    gap: 20px;                    
    padding: 18px 18px;
    border-radius: 12px;
    font-size: 18px;
    color: #E5E7EB;
    cursor: pointer;
    margin-bottom: 20px;
    background: transparent;
    transition: 0.15s ease;
}

div[role="radiogroup"] > label:hover {
    background: #114376;
    color: #FFFFFF;
}

div[role="radiogroup"] > label[aria-checked="true"],
div[role="radiogroup"] > label:has(input[type="radio"]:checked) {
    background-color: #03529C!important;
    color: #FFFFFF !important;
}

div[role="radiogroup"] > label[aria-checked="true"] span {
    color: #FFFFFF !important;
}

.big-card {
    background-color: #252B31;
    padding: 20px 25px;
    border-radius: 20px;
}
.metric-card {
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 10px 10px 10px 0;
}

.metric-value { font-size: 32px; font-weight: 700; }
.metric-label { font-size: 14px; opacity: 0.8; }
            
h1{
    color:#2587E2;
    font-size:46px;
    font-weight:700;
    margin:0 0 4px 0;
    }
            
h2,h3,h4,h5,h6 {
    color: #FFFFFF;
    font-family: "Inter", sans-serif;
    font-weight: 600;
}

p,span,label {
    color: #C9D1D9;
    font-family: "Inter", sans-serif;
    font-weight: 400;
}
            
.metric-card-low {
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 10px 20px 10px 0;
    width: 250px;
}

.metric-card-high {
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 10px 0 10px 80px;
    width: 250px;
}

.metric-card-change {
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 0 0 0 80px;
}
            
div[data-testid="stAppViewContainer"] div.stButton > button {
    background-color: #03529C;
    color: #FFFFFF;
    border-radius:20px;   
    padding: 15px 50px ;
    font-size: 33px;
    font-weight: 500;
    cursor: pointer;
    min-width: 170px;
    max-width: 171px;
    white-space: nowrap;  
}

div[data-testid="stAppViewContainer"] div.stButton > button:hover {
    background-color: #1976FF !important;
}
            
.h-tab-text {
    font-size: 17px;
    font-weight: 500;
    text-align: center;
    padding: 14px 50px;
    border-radius: 20px;
    cursor: pointer;
    transition: 0.1s ease;
    color: #DDE2F2;
    white-space: nowrap;
    display: inline-block;
}

.h-tab-active {
    background: #1976FF;
    color: #FFFFFF;
    border-color: #1976FF;
    font-size: 17px;
    font-weight: 500;
    text-align: center;
    padding: 15px 75px;
    border-radius: 20px;
    cursor: pointer;
    transition: 0.15s ease;
    white-space: nowrap;
    display: inline-block;
}
            
.small-card {
    background: #252B31;
    border-radius: 20px;
    padding: 20px 24px;
    font-size: 28px;
    color: #FFFFFF;
    font-weight: 700;
    font-family: inter, sans-serif;
}

.card-title {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 400;
    margin: 0 0 12px 0;
    font-family: inter, sans-serif;
}

.stSelectbox > div[data-baseweb="select"] * {
    color: #C9D1D9;
    background-color: #242A30;
    font-size: 14px;
}

.stSelectbox svg {
    color: #C9D1D9;
}

.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 5px 0;
    font-size: 13px;
}
.metric-label {
    color: #F5F5F5;
    font-size: 25px;
    font-family: inter, sans-serif;
    font-weight: 400;         
}
.metric-value {
    color: #F5F5F5;
    font-weight: 400;
    font-size: 25px;
    font-family: inter, sans-serif;
}
            
.sub-label {
    font-size: 26px;
    color: #D5D7F8;
    margin: 0 0 50px 0;
}

.empty-card-wrapper {
    margin-top: 28px;
}
.empty-card {
    background: #252B31;
    border-radius: 18px;
    padding: 40px 20px;
    text-align: center;
} 

.bottom-card {
    background: #252B31;
    border-radius: 20px;
    padding: 5px 5px;  
    font-size: 24px;
    font-weight: 
}

.chart-title {
    font-weight: 500;
    margin:0;
    padding : 4px;
    color: #2587E2;
}

.styled-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 8px;
    border-radius: 20px;
    overflow: hidden;
    }            
.styled-table th, .styled-table td {
    padding: 10px;
    text-align: center;
    }           
.styled-table th {
    background-color: #252B31;  
    color: #2587E2;  
    font-size: 20px;
    font-weight: 400px;
    }           
.styled-table td {
    background-color: #1E2328;  
    color: #FFFFFF; 
    font-size: 14px;
    border: 1px solid #6F6F6F;
    }
.styled-table tr:hover {
    background-color: #252B31; 
    }

div[data-testid="stDownloadButton"] > button {
    background-color: #2563EB;
    color: #FFFFFF;
    border-radius: 20px;
    border: none;
    padding: 0;
    font-size: 22px;
    font-weight: 500;
    width : 175px;
}
div[data-testid="stDownloadButton"] > button:disabled {
    background-color: #1976FF;
    color: #1976FF;
}

</style>
""", unsafe_allow_html=True)

st.write("")  

logo_path = BASE_DIR / "images" / "logo bri ai.png"
with st.sidebar:
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("### BBRI-AI")
    st.write("")
    
    label_to_value = {
        "⌂ Dashboard": "Dashboard",
        "〽 Market Overview": "Market Overview",
        "✴ Forecasting BBRI": "Forecasting BBRI",
    }

    selected_label = st.radio(
        "",
        list(label_to_value.keys()),
        label_visibility="collapsed",
    )
    menu = label_to_value[selected_label]

models = load_models(BASE_DIR)
preps = load_preprocessing(BASE_DIR)
data = load_data(BASE_DIR)

best_model = models.get("best_model")
feature_cols = preps.get("feature_cols")
df_prepared = data.get("prepared")

if menu == "Dashboard":
    render_dashboard(data)

elif menu == "Market Overview":
    render_market_overview(data)

elif menu == "Forecasting BBRI":
    st.markdown('<div class="page-panel">', unsafe_allow_html=True)
    render_forecasting_page()
    st.markdown('</div>', unsafe_allow_html=True)