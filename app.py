import streamlit as st
from pathlib import Path

from loaders import load_models, load_preprocessing, load_data
from dashboard_page import render_dashboard
from market_page import render_market_overview
from forecasting_page import render_forecasting_page
from forecasting_engine import run_forecast


st.set_page_config(
    page_title="BBRI-AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded", 
)
BASE_DIR = Path(__file__).parent

st.markdown(
    """
    <style>
        body { background-color: #1A1E23; }
        .main { background-color: #1A1E23; }
        [data-testid="stAppViewContainer"],
.block-container {
    background-color: #1A1E23!important;
}


section[data-testid="stSidebar"] {
    background-color: #072A4A;
    padding-top: 20px;
        }
}

h1,h2,h3,h4,h5,h6 {
    color: #FFFFFF;
    font-family: "Inter", sans-serif;
    font-weight: 600;
        }

p,span,label {
    color: #C9D1D9;
    font-family: "Inter", sans-serif;
    font-weight: 400;
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


.metric-value {
    font-size: 32px;
    font-weight: 700px;
    }

.metric-label {
    font-size: 14px;
    opacity: 0.8;
        }

.metric-card-low{
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 10px 40px 10px 0;
    width: 250px;
    }

.metric-card-high{
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 10px 20px 10px 40px;
    width: 250px;
    }


/* CARD untuk blok yang punya .price-title */
div[data-testid="stVerticalBlock"] div:has(> .price-title) {
    background:#252B31;
    border-radius:20px;
    padding:18px 20px 16px 20px;
    margin: 10px 20px 10px 135px;
}

/* Judul Price Trend */
.price-title {
    color:#2587E2;
    font-size:33px;
    font-family: Inter, sans-serif;
    font-weight:500;
    text-align:center;
    margin:0 0 10px 0;
}


div.stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #6B7280 !important;
        font-size: 17px;
        font-family: Inter, sans-serif;
        padding-bottom: 4px;
    }
    div.stButton > button:hover {
        color: #E5E7EB !important;
    }



div[role='radiogroup'] {
    display: flex!important;
    gap: 15px;
    font-size: 24px;
}

div[role='radiogroup'] > label {
    padding: 15px 20px;
    border-radius: 10px;
    font-size: 24px;
    color: #FFFFFF;
    display: center;  
}

div[role='radiogroup'] > label:hover {
     align-items: stretch;
     font-size: 24px;   
}

div[role='radiogroup'] > label[aria-checked="true"] {
    background-color: #03529C !important;
    color: #FFFFFF !important;
    border: 1px solid #03529C;
    align-items: flex-start;
}

div[role='radiogroup'] > label:has(input[type="radio"]:checked) {
    background-color: #03529C;
    padding : 20px 35px;
    border: 1px solid #03529C;
    align-items: flex-start;

}

/* Tombol Predict - BEFORE click (inactive) */
.predict-btn.inactive div.stButton > button {
    background-color: #2587E2 !important;
    color: white !important;
    border-radius: 18px !important;
    padding: 10px 32px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    border: none !important;
    cursor: pointer;
    width: 100% !important; /* tidak melebar aneh */
    transition: 0.25s;
}

/* Tombol Predict - AFTER click (active) */
.predict-btn.active div.stButton > button {
    background-color: #1f6ac4 !important;   /* biru lebih gelap */
    color: white !important;
    border-radius: 18px !important;
    padding: 10px 32px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    border: none !important;
    width: 100% !important;
}

/* Hover state (optional) */
.predict-btn.inactive div.stButton > button:hover {
    background-color: #2f8ef0 !important;
}

.predict-btn.active div.stButton > button:hover {
    background-color: #1d5faf !important;
}



    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    logo_path = BASE_DIR / "images" / "logo bri ai.png"
    if logo_path.exists():
        st.image(str(logo_path), use_container_width=True)
    else:
        st.markdown("### BBRI-AI")

    default_menu = st.session_state.get("menu", "Dashboard")

    menu = st.radio(
        "", 
        ["Dashboard", "Market Overview", "Forecasting BBRI"],
        index=["Dashboard", "Market Overview", "Forecasting BBRI"].index(default_menu),
        key="menu_radio",
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["menu"] = menu



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
