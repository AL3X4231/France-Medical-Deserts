"""
Data Transformation & Feature Engineering
utils/prep.py - Prepares commune and department datasets
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
from utils.io import (
    RAW_DATA_PATH,
    PROCESSED_COMMUNES_PATH,
    PROCESSED_DEPTS_PATH,
    PROCESSED_DIR,
    ensure_directories,
    download_raw_dataset,
)
from utils.departments import DEPARTMENTS
from utils.config import APL_CRITICAL_THRESHOLD

NATIONAL_METRICS_PATH = os.path.join(PROCESSED_DIR, "national_summary.json")


def extract_dept_code(insee_code: str) -> str:
    """Extract 2-character or 3-character department code from INSEE commune code."""
    s = str(insee_code).strip().zfill(5)
    if s.startswith("2A") or s.startswith("2a"):
        return "2A"
    if s.startswith("2B") or s.startswith("2b"):
        return "2B"
    if s.startswith("97"):
        return s[:3]
    return s[:2]


def process_raw_excel():
    """Read raw DREES Excel and generate parquet caches for communes & departments."""
    ensure_directories()
    download_raw_dataset()

    years = [2022, 2023, 2024]
    commune_frames = []

    for year in years:
        sheet_name = f"APL {year}"
        df = pd.read_excel(RAW_DATA_PATH, sheet_name=sheet_name, skiprows=8)

        # Drop description row and clean rows
        df_clean = df.dropna(subset=["Code commune INSEE"]).copy()
        # Keep rows with valid insee code
        df_clean = df_clean[df_clean["Code commune INSEE"].astype(str).str.len() >= 4].copy()

        # Rename columns standardly
        cols = df_clean.columns.tolist()
        rename_map = {
            cols[0]: "insee_code",
            cols[1]: "commune_name",
            cols[2]: "apl_all",
            cols[3]: "apl_under_65",
            cols[4]: "apl_under_62",
            cols[5]: "apl_under_60",
            cols[6]: "pop_standardized",
            cols[7]: "pop_total",
        }
        df_clean = df_clean.rename(columns=rename_map)

        # Ensure correct numeric types
        for col in ["apl_all", "apl_under_65", "apl_under_62", "apl_under_60", "pop_standardized", "pop_total"]:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0.0)

        df_clean["insee_code"] = df_clean["insee_code"].astype(str).str.strip().str.zfill(5)
        df_clean["year"] = int(year)

        # Department mapping
        df_clean["dept_code"] = df_clean["insee_code"].apply(extract_dept_code)
        df_clean["dept_name"] = df_clean["dept_code"].apply(lambda c: DEPARTMENTS.get(c, {}).get("name", f"Dept {c}"))
        df_clean["region_name"] = df_clean["dept_code"].apply(lambda c: DEPARTMENTS.get(c, {}).get("region", "Autre"))

        # Feature engineering
        df_clean["is_desert"] = df_clean["apl_all"] < APL_CRITICAL_THRESHOLD
        df_clean["deficit"] = np.maximum(0.0, APL_CRITICAL_THRESHOLD - df_clean["apl_all"])
        df_clean["pop_in_desert"] = np.where(df_clean["is_desert"], df_clean["pop_total"], 0.0)

        commune_frames.append(df_clean)

    # Consolidated communes dataframe (saving both parquet and CSV for transparency)
    communes_df = pd.concat(commune_frames, ignore_index=True)
    communes_df.to_parquet(PROCESSED_COMMUNES_PATH, index=False)
    communes_df.to_csv(os.path.join(PROCESSED_DIR, "apl_communes.csv"), index=False)

    # Aggregate department-level metrics
    dept_records = []
    for (dept_code, year), group in communes_df.groupby(["dept_code", "year"]):
        sum_pop_std = group["pop_standardized"].sum()
        weighted_apl = (group["apl_all"] * group["pop_standardized"]).sum() / sum_pop_std if sum_pop_std > 0 else 0.0
        weighted_apl_under_60 = (group["apl_under_60"] * group["pop_standardized"]).sum() / sum_pop_std if sum_pop_std > 0 else 0.0
        
        cliff_pct = ((weighted_apl - weighted_apl_under_60) / weighted_apl * 100.0) if weighted_apl > 0 else 0.0

        total_pop = group["pop_total"].sum()
        desert_pop = group["pop_in_desert"].sum()
        pct_pop_desert = (desert_pop / total_pop * 100.0) if total_pop > 0 else 0.0

        total_communes = len(group)
        desert_communes = int(group["is_desert"].sum())
        pct_desert_communes = (desert_communes / total_communes * 100.0) if total_communes > 0 else 0.0

        dept_info = DEPARTMENTS.get(dept_code, {"name": f"Dept {dept_code}", "region": "Autre"})

        dept_records.append({
            "dept_code": dept_code,
            "dept_name": dept_info["name"],
            "region_name": dept_info["region"],
            "year": int(year),
            "weighted_apl": round(float(weighted_apl), 3),
            "weighted_apl_under_60": round(float(weighted_apl_under_60), 3),
            "retirement_cliff_pct": round(float(cliff_pct), 2),
            "total_pop": int(round(total_pop)),
            "desert_pop": int(round(desert_pop)),
            "pct_pop_in_desert": round(float(pct_pop_desert), 2),
            "total_communes": total_communes,
            "desert_communes": desert_communes,
            "pct_desert_communes": round(float(pct_desert_communes), 2),
            "is_dept_desert": bool(weighted_apl < APL_CRITICAL_THRESHOLD),
        })

    depts_df = pd.DataFrame(dept_records)

    # Compute two-year trajectory indicators against 2022 baseline
    b2022 = depts_df[depts_df["year"] == 2022].set_index("dept_code")[["weighted_apl", "pct_pop_in_desert"]]
    depts_df = depts_df.merge(b2022, on="dept_code", suffixes=("", "_base2022"), how="left")
    depts_df["delta_apl_since_2022"] = (depts_df["weighted_apl"] - depts_df["weighted_apl_base2022"]).round(3)
    depts_df["delta_desert_pct_since_2022"] = (depts_df["pct_pop_in_desert"] - depts_df["pct_pop_in_desert_base2022"]).round(2)
    depts_df = depts_df.drop(columns=["weighted_apl_base2022", "pct_pop_in_desert_base2022"])

    depts_df.to_parquet(PROCESSED_DEPTS_PATH, index=False)
    depts_df.to_csv(os.path.join(PROCESSED_DIR, "apl_departments.csv"), index=False)

    # National baselines
    national_summary = {}
    for year, group in communes_df.groupby("year"):
        sum_pop_std = group["pop_standardized"].sum()
        nat_apl = (group["apl_all"] * group["pop_standardized"]).sum() / sum_pop_std if sum_pop_std > 0 else 0.0
        nat_apl_u60 = (group["apl_under_60"] * group["pop_standardized"]).sum() / sum_pop_std if sum_pop_std > 0 else 0.0
        nat_total_pop = group["pop_total"].sum()
        nat_desert_pop = group["pop_in_desert"].sum()

        national_summary[str(year)] = {
            "weighted_apl": round(float(nat_apl), 3),
            "weighted_apl_under_60": round(float(nat_apl_u60), 3),
            "retirement_cliff_pct": round(float((nat_apl - nat_apl_u60) / nat_apl * 100.0), 2),
            "total_pop": int(round(nat_total_pop)),
            "desert_pop": int(round(nat_desert_pop)),
            "pct_pop_in_desert": round(float(nat_desert_pop / nat_total_pop * 100.0), 2),
            "total_communes": len(group),
            "desert_communes": int(group["is_desert"].sum()),
            "pct_desert_communes": round(float(group["is_desert"].sum() / len(group) * 100.0), 2),
        }

    with open(NATIONAL_METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(national_summary, f, indent=2)

    return communes_df, depts_df, national_summary


@st.cache_data(show_spinner=False)
def load_all_data():
    """Load cached parquet data with st.cache_data for instant performance."""
    if not os.path.exists(PROCESSED_COMMUNES_PATH) or not os.path.exists(PROCESSED_DEPTS_PATH):
        return process_raw_excel()

    communes_df = pd.read_parquet(PROCESSED_COMMUNES_PATH)
    depts_df = pd.read_parquet(PROCESSED_DEPTS_PATH)
    with open(NATIONAL_METRICS_PATH, "r", encoding="utf-8") as f:
        national_summary = json.load(f)

    return communes_df, depts_df, national_summary
