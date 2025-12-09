import streamlit as st
import pandas as pd
import joblib
import pickle
from pathlib import Path

@st.cache_resource
def load_models(base_dir: Path):
    models_dir = base_dir / "models"
    best_model_path = models_dir / "best_model.pkl"
    lightgbm_path = models_dir / "model_lightgbm.pkl"
    best_model = None
    lightgbm_model = None
    if best_model_path.exists():
        best_model = joblib.load(best_model_path)
    if lightgbm_path.exists():
        lightgbm_model = joblib.load(lightgbm_path)
    return {
        "best_model": best_model,
        "lightgbm": lightgbm_model
    }


@st.cache_resource
def load_preprocessing(base_dir: Path):
    prep_dir = base_dir / "preprocessing"
    feature_cols_path = prep_dir / "feature_columns.pkl"
    scaler_pack_path = prep_dir / "scaler_pack.pkl"
    feature_cols = None
    scaler_pack = None
    if feature_cols_path.exists():
        with open(feature_cols_path, "rb") as f:
            feature_cols = pickle.load(f)
    if scaler_pack_path.exists():
        with open(scaler_pack_path, "rb") as f:
            scaler_pack = pickle.load(f)
    return {
        "feature_cols": feature_cols,
        "scaler_pack": scaler_pack
    }


@st.cache_data
def load_data(base_dir: Path):
    data_dir = base_dir / "data"
    prep_dir = base_dir / "preprocessing"
    data_raw = None
    df_prepared = None
    df_train = None
    df_val = None
    df_test = None
    eval_results = None
    if (data_dir / "data_saham_bbri_jk.csv").exists():
        data_raw = pd.read_csv(data_dir / "data_saham_bbri_jk.csv")
    if (prep_dir / "df_prepared_bbri.csv").exists():
        df_prepared = pd.read_csv(prep_dir / "df_prepared_bbri.csv")
    if (data_dir / "train_bbri.csv").exists():
        df_train = pd.read_csv(data_dir / "train_bbri.csv")
    if (data_dir / "val_bbri.csv").exists():
        df_val = pd.read_csv(data_dir / "val_bbri.csv")
    if (data_dir / "test_bbri.csv").exists():
        df_test = pd.read_csv(data_dir / "test_bbri.csv")
    if (data_dir / "model_evaluation_results.csv").exists():
        eval_results = pd.read_csv(data_dir / "model_evaluation_results.csv")
    return {
        "raw": data_raw,
        "prepared": df_prepared,
        "train": df_train,
        "val": df_val,
        "test": df_test,
        "eval": eval_results
    }