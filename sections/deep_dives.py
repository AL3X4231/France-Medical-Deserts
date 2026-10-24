"""
Section 3: Deep Dives & The "Retirement Cliff"
sections/deep_dives.py - Intra-departmental distributions, correlation analysis, and regional rankings
"""

import streamlit as st
import pandas as pd
from utils.viz import (
    plot_distribution_box,
    plot_correlation_scatter,
    plot_small_multiples_regions,
)
from utils.config import APL_CRITICAL_THRESHOLD


def render(communes_df: pd.DataFrame, depts_df: pd.DataFrame, selected_year: int, selected_regions: list):
    """Render Section 3: In-depth statistical drilldowns and correlation analysis."""
    st.markdown("## Deep Dives & The Impending Care Cliff")

    # One-sentence headline insight
    st.info(
        "**Headline Insight**: *Territorial averages mask acute localized inequality: even within average-ranking departments, over 40% of peripheral communes are severe care deserts, while the impending retirement of doctors aged ≥ 60 threatens to collapse primary access by another 25% to 40%.*"
    )

    tab1, tab2, tab3 = st.tabs([
        "Intra-Departmental Inequality",
        "The Retirement Cliff (Doctor Aging)",
        "Regional Rankings & Commune Explorer",
    ])

    with tab1:
        st.subheader("Distribution & The Hidden Pockets of Scarcity")
        st.markdown(
            """
            Evaluating a department purely by its mean APL creates an illusion of security. 
            In reality, healthcare resources cluster in urban centers, leaving rural peripheral communes deeply underserved.
            """
        )

        col_sel, col_box = st.columns([1, 2.2])
        with col_sel:
            active_depts = sorted(depts_df[depts_df["year"] == selected_year]["dept_name"].unique())
            default_pick = "Mayenne" if "Mayenne" in active_depts else active_depts[0]
            dept_choice = st.selectbox("Inspect Commune Spread in Department:", active_depts, index=active_depts.index(default_pick))

            # Department mini stats
            d_row = depts_df[(depts_df["dept_name"] == dept_choice) & (depts_df["year"] == selected_year)].iloc[0]
            st.metric("Department Mean APL", f"{d_row['weighted_apl']:.2f}")
            st.metric("% Communes in Desert (< 2.5)", f"{d_row['pct_desert_communes']:.1f}%")
            st.metric("Pop. in Desert Communes", f"{d_row['desert_pop']:,d} hab.")

        with col_box:
            fig_box = plot_distribution_box(communes_df, dept_choice, year=selected_year)
            st.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        st.subheader("The Demographic Trap: APL vs. Doctor Age Exposure")
        st.markdown(
            """
            This scatter plot maps each department along two vital axes:
            - **Horizontal Axis**: The percentage of primary care consultation capacity currently held by general practitioners aged **60 and older** (*The Retirement Cliff*).
            - **Vertical Axis**: Current weighted primary care access (**APL**).
            
            Departments located in the **red quadrant (bottom-right)** face a **double penalty**: their healthcare access is already sub-par, and they depend most heavily on doctors who will retire in the coming years.
            """
        )

        fig_scatter = plot_correlation_scatter(depts_df, year=selected_year)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with tab3:
        st.subheader("Regional Comparison (Small Multiples Pattern)")
        fig_regions = plot_small_multiples_regions(depts_df, year=selected_year)
        st.plotly_chart(fig_regions, use_container_width=True)

        st.markdown("---")
        st.subheader("Commune-Level Priority Watchlist")
        st.markdown("Inspect the most vulnerable communes (lowest APL) to prioritize public health interventions:")

        # Filter communes
        sub_c = communes_df[communes_df["year"] == selected_year].copy()
        if selected_regions:
            sub_c = sub_c[sub_c["region_name"].isin(selected_regions)]

        # Search bar
        search_query = st.text_input("Filter by Commune Name or INSEE Code:", "").strip().lower()
        if search_query:
            sub_c = sub_c[sub_c["commune_name"].str.lower().str.contains(search_query) | sub_c["insee_code"].str.contains(search_query)]

        # Show critical first
        display_cols = ["insee_code", "commune_name", "dept_name", "region_name", "apl_all", "apl_under_60", "pop_total", "is_desert"]
        table_view = sub_c[display_cols].sort_values("apl_all", ascending=True).head(50)

        st.dataframe(
            table_view.rename(columns={
                "insee_code": "INSEE Code",
                "commune_name": "Commune",
                "dept_name": "Department",
                "region_name": "Region",
                "apl_all": "APL (All GPs)",
                "apl_under_60": "APL (GPs < 60)",
                "pop_total": "Total Population",
                "is_desert": "Medical Desert?",
            }),
            use_container_width=True,
            hide_index=True,
        )
