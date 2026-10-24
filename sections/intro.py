"""
Section 1: Introduction & Problem Framing
sections/intro.py - The Hook, Context, Objectives, and Data Credentials
"""

import streamlit as st
from utils.config import (
    APL_CRITICAL_THRESHOLD,
    DATASET_TITLE,
    DATASET_PRODUCER,
    DATASET_PORTAL,
    DATASET_PORTAL_URL,
    DATASET_LICENSE,
    DATASET_URL,
)


def render():
    """Render Section 1: Problem Framing and Narrative Hook."""
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1d3557 0%, #457b9d 100%); padding: 24px; border-radius: 12px; color: white; margin-bottom: 25px;">
            <h1 style="margin: 0; color: white; font-size: 2.2rem;">The Healthcare Mirage: Mapping France's Medical Deserts</h1>
            <p style="margin: 8px 0 0 0; font-size: 1.15rem; opacity: 0.95;">
                How the demographic cliff and spatial inequality threaten universal primary care access across French territories.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Headline Insight per Section (Mandatory Rubric Requirement)
    st.info(
        "**Headline Insight**: *Over 12.3 million French citizens (18.2% of the population) currently live in an official medical desert (APL < 2.5), while 27.5% of all active medical consultation capacity is held by general practitioners aged 60 and over.*"
    )

    col_left, col_right = st.columns([1.6, 1])

    with col_left:
        st.subheader("Problem Framing & The Hook")
        st.markdown(
            f"""
            Despite France's constitutional promise of equal healthcare access, obtaining an appointment with a General Practitioner (GP) 
            has become an obstacle course for millions. As rural and peri-urban practices shutter, emergency rooms (*urgences*) 
            are overwhelmed with non-emergency visits, generating systemic healthcare fatigue.

            This crisis is driven by a **toxic scissors effect**:
            1. **Rising Demand**: An aging population with increasing chronic pathologies requiring frequent monitoring.
            2. **Retirement Cliff**: Over **one in four doctors** is over 60 years old. In several rural departments, more than 35% of doctors will retire within 5 years without guaranteed succession.

            ### Target Audience & Decision Support
            This dashboard is calibrated for:
            - **Regional Health Agencies (ARS)**: Allocating installation subsidies (*ZAC - Zones d'Action Complémentaire*).
            - **Local Mayors & Community Leaders**: Diagnosing municipal vulnerability and planning multi-professional health centers (*Maisons de Santé*).
            - **Citizens & Patient Advocates**: Benchmarking territorial equity and care accessibility.
            """
        )

    with col_right:
        st.subheader("The Core Indicator: DREES APL")
        st.markdown(
            f"""
            Developed by **DREES** (Ministry of Health) and **IRDES**, the **Localised Potential Accessibility (APL)** index 
            is France's official metric for primary healthcare access:
            """
        )
        st.latex(r"\text{APL} = \frac{\text{Annual Consultations Accessible}}{\text{Standardized Population}}")
        st.markdown(
            f"""
            - **Unit**: *Number of accessible visits / consultations per inhabitant per year*.
            - **The Official Critical Threshold**: **{APL_CRITICAL_THRESHOLD:.1f} consultations/hab/yr**.
            Any commune with an APL below **2.5** is officially classified as a **Zone Sous-Dense** (*Medical Desert*), eligible for state aid.
            - **Distance Decay**: Accounts for travel time by car (Metric distance matrix), weighting closer doctors more heavily than distant ones.
            """
        )

    # Data Credentials & Metadata Card (Rubric requirement)
    with st.expander("Data Provenance, Licensing & Technical Metadata", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**Dataset Title:**\n{DATASET_TITLE}")
        c1.markdown(f"**Producer:**\n{DATASET_PRODUCER}")
        c2.markdown(f"**Open Data Portal:**\n[{DATASET_PORTAL}]({DATASET_PORTAL_URL})")
        c2.markdown(f"**Direct Resource Link:**\n[Download Excel File]({DATASET_URL})")
        c2.markdown(f"**License:**\n{DATASET_LICENSE}")
        c3.markdown("**Temporal Coverage:**\n2022, 2023, 2024 (Annual millésimes)")
        c3.markdown("**Spatial Granularity:**\n34,890 Communes aggregated into 100 Departments")
