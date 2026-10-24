"""
Main Streamlit Application Entrypoint
app.py - Data Storytelling Dashboard: Mapping France's Medical Deserts
EFREI Paris - Individual Student Project 2026
"""

import streamlit as st
from utils.config import (
    STUDENT_NAME,
    STUDENT_ID,
    STUDENT_GROUP,
    PROFESSOR_NAME,
    APP_TITLE,
    APP_SUBTITLE,
    APP_HASHTAGS,
    DATASET_TITLE,
    DATASET_PORTAL,
    DATASET_PORTAL_URL,
    DATASET_LICENSE,
)
from utils.prep import load_all_data
from utils.departments import REGIONS
from sections import intro, overview, deep_dives, conclusions

# Configure page layout and meta
st.set_page_config(
    page_title=f"{STUDENT_NAME} - Data Stories 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished aesthetic and typography
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.08) !important;
        border-radius: 10px !important;
        padding: 14px 18px !important;
        border: 1px solid rgba(128, 128, 128, 0.22) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.06) !important;
    }
    div[data-testid="stMetricLabel"] * {
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stMetricValue"] * {
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def main():
    # Load cached data
    with st.spinner("Loading healthcare datasets..."):
        communes_df, depts_df, national_summary = load_all_data()

    # Sidebar Navigation & Filters
    with st.sidebar:
        st.markdown(
            f"""
            <div style="background-color: #f1f5f9; padding: 14px; border-radius: 8px; border-left: 4px solid #1d3557; margin-bottom: 16px;">
                <div style="font-size: 0.85rem; color: #64748b; font-weight: 600;">EFREI PARIS • DATA STORIES 2026</div>
                <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a;">{STUDENT_NAME}</div>
                <div style="font-size: 0.85rem; color: #334155;">ID: <b>{STUDENT_ID}</b> | Group: <b>{STUDENT_GROUP}</b></div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">Prof: {PROFESSOR_NAME}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.header("Story Navigation")
        nav_mode = st.radio(
            "Select Chapter:",
            options=[
                "1. The Problem (Hook & Framing)",
                "2. Territorial Radiography (Map & Macro)",
                "3. Deep Dives (Inequality & Aging)",
                "4. Policy Sandbox & Conclusions",
                "Full Story (Continuous Reading)",
            ],
            index=4,
        )

        st.markdown("---")
        st.header("Data Filters")

        selected_year = st.select_slider(
            "Observation Year:",
            options=[2022, 2023, 2024],
            value=2024,
            help="Select the DREES annual millésime to analyze temporal evolution.",
        )

        selected_regions = st.multiselect(
            "Filter by French Region(s):",
            options=REGIONS,
            default=[],
            help="Leave empty to analyze all regions nationwide.",
        )

        st.markdown("---")
        st.caption(
            f"**Data Source**: {DATASET_TITLE}\n\n"
            f"**Portal**: [{DATASET_PORTAL}]({DATASET_PORTAL_URL})\n\n"
            f"**License**: {DATASET_LICENSE}\n\n"
            f"*{APP_HASHTAGS}*"
        )

    # Narrative flow rendering
    if nav_mode == "1. The Problem (Hook & Framing)":
        intro.render()
    elif nav_mode == "2. Territorial Radiography (Map & Macro)":
        overview.render(depts_df, national_summary, selected_year, selected_regions)
    elif nav_mode == "3. Deep Dives (Inequality & Aging)":
        deep_dives.render(communes_df, depts_df, selected_year, selected_regions)
    elif nav_mode == "4. Policy Sandbox & Conclusions":
        conclusions.render(communes_df, depts_df, selected_year)
    else:
        # Full continuous storytelling experience
        intro.render()
        st.markdown("<br><hr style='border: 1px solid #e2e8f0;'><br>", unsafe_allow_html=True)
        overview.render(depts_df, national_summary, selected_year, selected_regions)
        st.markdown("<br><hr style='border: 1px solid #e2e8f0;'><br>", unsafe_allow_html=True)
        deep_dives.render(communes_df, depts_df, selected_year, selected_regions)
        st.markdown("<br><hr style='border: 1px solid #e2e8f0;'><br>", unsafe_allow_html=True)
        conclusions.render(communes_df, depts_df, selected_year)

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; color: #64748b; font-size: 0.85rem; padding: 20px;">
            <b>EFREI Paris</b> — Data Storytelling Project 2026 | Built by <b>{STUDENT_NAME}</b> (ID: {STUDENT_ID}, {STUDENT_GROUP})<br>
            Supervised by {PROFESSOR_NAME} ({DATASET_PORTAL}) | {APP_HASHTAGS}
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
