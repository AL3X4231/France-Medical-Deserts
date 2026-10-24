"""
Data Ingestion & Caching Module
utils/io.py - Handles downloading, local caching, and GeoJSON loading
"""

import os
import json
import urllib.request
import pandas as pd
import streamlit as st
from utils.config import DATASET_URL

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed")
GEOJSON_PATH = os.path.join(RAW_DIR, "france_departments.geojson")
RAW_DATA_PATH = os.path.join(RAW_DIR, "indicateur_d_apl_aux_medecins_generalistes.xlsx")
PROCESSED_COMMUNES_PATH = os.path.join(PROCESSED_DIR, "apl_communes.parquet")
PROCESSED_DEPTS_PATH = os.path.join(PROCESSED_DIR, "apl_departments.parquet")

GEOJSON_URL = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"


def ensure_directories():
    """Ensure data/raw and data/processed directories exist."""
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)


def download_raw_dataset(progress_callback=None):
    """Download the official DREES Excel dataset if not already cached locally."""
    ensure_directories()
    if not os.path.exists(RAW_DATA_PATH) or os.path.getsize(RAW_DATA_PATH) < 1000:
        headers = {"User-Agent": "Mozilla/5.0 (EFREI Data Storytelling Dashboard)"}
        req = urllib.request.Request(DATASET_URL, headers=headers)
        with urllib.request.urlopen(req) as resp, open(RAW_DATA_PATH, "wb") as out_file:
            total_size = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            block_size = 1024 * 128
            while True:
                chunk = resp.read(block_size)
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total_size > 0:
                    progress_callback(downloaded / total_size)


def download_geojson():
    """Download French departments GeoJSON for offline/fast choropleth mapping."""
    ensure_directories()
    if not os.path.exists(GEOJSON_PATH) or os.path.getsize(GEOJSON_PATH) < 1000:
        headers = {"User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(GEOJSON_URL, headers=headers)
        with urllib.request.urlopen(req) as resp, open(GEOJSON_PATH, "wb") as out_file:
            out_file.write(resp.read())


@st.cache_data(show_spinner=False)
def load_geojson():
    """Load cached GeoJSON with st.cache_data."""
    download_geojson()
    with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
