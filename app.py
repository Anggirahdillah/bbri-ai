import streamlit as st
from pathlib import Path

from loaders import load_models, load_preprocessing, load_data
from dashboard_page import render_dashboard
from market_page import render_market_overview
from forecasting_page import render_forecasting_page
from forecasting_engine import run_forecast

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="BBRI-AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS — FIX supaya tdk hilang setelah refresh / interaksi
st.markdown("""
<style>
body { background-color: #1A1E23; }
.main { background-color: #1A1E23; }

[data-testid="stAppViewContainer"],
.block-container {
    background-color: #1A1E23 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #072A4A;
    padding-top: 20px;
}

h1{
    color:#2587E2;
    font-size:46px;
    font-weight:700;
    margin:0 0 4px 0;
    }
            
/* Heading text */
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

/* 📌 Card components */
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
    margin: 10px 0 10px 20px;
    width: 250px;
}

.metric-card-change {
    background-color: #252B31;
    padding: 10px 25px;
    border-radius: 20px;
    margin: 0 0 0 50px;
}

.metric-value { font-size: 32px; font-weight: 700; }
.metric-label { font-size: 14px; opacity: 0.8; }

/* 📌 BLOCK Price Panel */
div[data-testid="stVerticalBlock"] div:has(> .price-title) {
    background:#252B31;
    border-radius:20px;
    padding:18px 20px 16px 20px;
    margin: 10px 20px 10px 135px;
}
.price-title {
    color:#2587E2;
    font-size:33px;
    font-family: Inter, sans-serif;
    font-weight:500;
    text-align:center;
    margin:0 0 10px 0;
}

/* 📌 Sidebar Buttons (KHUSUS di sidebar aja) */
section[data-testid="stSidebar"] div.stButton > button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #6B7280 !important;
    font-size: 17px;
    font-family: Inter, sans-serif;
    padding-bottom: 4px;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    color: #E5E7EB !important;
}


/* 📌 Radio Menu */
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
}
div[role='radiogroup'] > label[aria-checked="true"],
div[role='radiogroup'] > label:has(input[type="radio"]:checked) {
    background-color: #03529C !important;
    color: #FFFFFF !important;
    padding: 20px 35px;
    border: 1px solid #03529C;
}
            
/* Kartu kecil (Today Overview, Forecast Summary, Model Eval) */
.small-card {
    background: #252B31;
    border-radius: 20px;
    padding: 20px 24px;
    font-size: 28px;
    color: #FFFFFF;
    font-weight: 700;
    font-family: inter, sans-serif;
}

/* Judul di dalam kartu (biru besar seperti gambar) */
.card-title {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 400;
    margin: 0 0 12px 0;
    font-family: inter, sans-serif;
}

/* Baris metric kiri-kanan */
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

/* CARD BAWAH (chart + tabel) */
.bottom-card {
    background: #252B31;
    border-radius: 20px;
    padding: 10px 10px;
    height: 100%;
}
.chart-title {
    font-size: 24px;
    font-weight: 500;
    color: #2587E2;
            
}

/* EMPTY STATE */
.empty-card-wrapper {
    margin-top: 28px;
}
.empty-card {
    background: #252B31;
    border-radius: 18px;
    padding: 40px 20px;
    text-align: center;
}



/* Auto-update dibuat seperti pill */
.auto-checkbox div[data-testid="stCheckbox"] > label {
    background-color: #020617;
    border-radius: 999px;
    padding: 8px 16px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    border: 1px solid #2D3648;
}
.auto-checkbox div[data-testid="stCheckbox"] label p {
    margin-bottom: 0px;
}
.auto-checkbox div[data-testid="stCheckbox"] svg {
    width: 14px;
    height: 14px;
}

/* Caption checkbox */
div[data-testid="stCheckbox"] label {
    color: #FFFFFF;
    font-size: 14px;
}


/* Horizon chips (radio) */
.horizon-row {
    margin-top: 0;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] {
    display: flex;
    gap: 5px;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label {
    padding: 6px 18px;
    border-radius: 999px;
    font-size: 14px;
    background-color: #020617;
    color: #E5E7EB;
    cursor: pointer;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label:hover {
    background-color: #0F172A;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] > label:has(input[type="radio"]:checked) {
    background-color: #2563EB !important;
    border-color: #2563EB !important;
    color: #FFFFFF !important;
}
div[data-testid="stRadio"][aria-label="forecast-horizon"] div[role='radiogroup'] input[type="radio"] {
    opacity: 0;
    position: absolute;
    pointer-events: none;
}

/* Download button biru */
div[data-testid="stDownloadButton"] > button {
    background-color: #2563EB;
    color: #FFFFFF;
    border-radius: 999px;
    border: none;
    padding: 8px 24px;
    font-size: 14px;
    font-weight: 500;
}
div[data-testid="stDownloadButton"] > button:disabled {
    background-color: #111827;
    color: #9CA3AF;
}

/* Sub label kecil (Last updated, dll) */
.sub-label {
    font-size: 26px;
    color: #D5D7F8;
}
/* ================== MAIN BUTTON STYLE (PREDICT / KEMBALI DLL) ================== */
div[data-testid="stAppViewContainer"] div.stButton > button {
    background-color: #03529C;
    color: #FFFFFF;
    border-radius:20px;       /* pill */
    padding: 15px 50px ;
    font-size: 33px;
    font-weight: 500;
    cursor: pointer;
    min-width: 170px;
    max-width: 171px;
    white-space: nowrap;  
}

/* hover */
div[data-testid="stAppViewContainer"] div.stButton > button:hover {
    background-color: #1f6bb6 !important;
}


/* STYLE DASAR SEMUA SEGMENT (PASIF) */
.h-tab-text {
    font-size: 17px;
    font-weight: 500;
    text-align: center;
    padding: 14px 50px;            /* jangan 80px lagi biar ga numpuk */
    border-radius: 20px;         /* biar ujung bulat, nyatu di dalam kapsul */
    cursor: pointer;
    transition: 0.15s ease;
    color: #DDE2F2;               /* putih keabu-abuan */
    white-space: nowrap;          /* teks 1D / 1W ga turun baris */
    display: inline-block;
}

/* SEGMENT AKTIF */
.h-tab-active {
    background: #1976FF;
    color: #FFFFFF;
    border-color: #1976FF;
    font-size: 17px;
    font-weight: 500;
    text-align: center;
    padding: 15px 75px;            /* jangan 80px lagi biar ga numpuk */
    border-radius: 20px;         /* biar ujung bulat, nyatu di dalam kapsul */
    cursor: pointer;
    transition: 0.15s ease;       /* putih keabu-abuan */
    white-space: nowrap;          /* teks 1D / 1W ga turun baris */
    display: inline-block;

}

            /* ================= HORIZON BUTTON CHIPS ================= */
.horizon-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 10px;
}

/* wrapper chips (BEBAS dari predict-btn) */
.hz-chip,
.hz-chip-active {
    display: inline-block;
    width: 100%;
}

/* style dasar semua tombol horizon */
.hz-chip div.stButton > button,
.hz-chip-active div.stButton > button {
    border-radius: 14px;
    padding: 10px 26px;
    font-size: 17px;
    font-weight: 500;
    border: 1px solid #3B4450;
    background: #111827;
    color: #E5E7EB;
    cursor: pointer;
    transition: 0.15s;
    width: 100%;
}

/* tombol horizon aktif: biru */
.hz-chip-active div.stButton > button {
    background: #1976FF;
    border-color: #1976FF;
    color: #FFFFFF;
}

/* hover untuk semua horizon button */
.hz-chip div.stButton > button:hover,
.hz-chip-active div.stButton > button:hover {
    filter: brightness(1.1);
}

</style>
""", unsafe_allow_html=True)


# Trick anti-hilang saat rerender
st.write("")  


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
    
