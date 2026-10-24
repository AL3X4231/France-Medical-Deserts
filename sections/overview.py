"""
Section 2: Overview & Territorial Radiography
sections/overview.py - KPI header with deltas, interactive Choropleth Map, and temporal trajectories
"""

import streamlit as st
import pandas as pd
from utils.viz import plot_choropleth_map, plot_timeseries_evolution
from utils.io import load_geojson
from utils.config import APL_CRITICAL_THRESHOLD


def render(depts_df: pd.DataFrame, nat_summary: dict, selected_year: int, selected_regions: list):
    """Render Section 2: Macro KPIs, Choropleth Map, and Macro Trajectories."""
    st.markdown("## Territorial Radiography & Macro Trends")

    # Filter data according to sidebar selections
    year_str = str(selected_year)
    nat_base = nat_summary[year_str]

    filtered_depts = depts_df[depts_df["year"] == selected_year].copy()
    if selected_regions:
        filtered_depts = filtered_depts[filtered_depts["region_name"].isin(selected_regions)]

    # Compute filtered KPIs
    tot_pop_filtered = filtered_depts["total_pop"].sum()
    desert_pop_filtered = filtered_depts["desert_pop"].sum()
    pct_desert_filtered = (desert_pop_filtered / tot_pop_filtered * 100.0) if tot_pop_filtered > 0 else 0.0

    # Weighted APL of filtered set
    sum_pop_std = (filtered_depts["weighted_apl"] * filtered_depts["total_pop"]).sum()
    avg_apl_filtered = (sum_pop_std / tot_pop_filtered) if tot_pop_filtered > 0 else 0.0

    # Population-weighted retirement cliff for filtered set
    tot_apl_pop = (filtered_depts["weighted_apl"] * filtered_depts["total_pop"]).sum()
    u60_apl_pop = (filtered_depts["weighted_apl_under_60"] * filtered_depts["total_pop"]).sum()
    weighted_cliff_filtered = (((tot_apl_pop - u60_apl_pop) / tot_apl_pop) * 100.0) if tot_apl_pop > 0 else 0.0

    has_region_filter = bool(selected_regions)
    base_2022 = nat_summary["2022"]

    if has_region_filter:
        # Comparing filtered region vs national average for the same year
        delta_apl_str = f"{avg_apl_filtered - nat_base['weighted_apl']:+.2f} vs National Avg ({nat_base['weighted_apl']:.2f})"
        delta_desert_str = f"{pct_desert_filtered - nat_base['pct_pop_in_desert']:+.1f}% vs National ({nat_base['pct_pop_in_desert']:.1f}%)"
        delta_pop_str = f"{len(filtered_depts)} departments in selection"
        delta_cliff_str = f"{weighted_cliff_filtered - nat_base['retirement_cliff_pct']:+.1f}% vs National ({nat_base['retirement_cliff_pct']:.1f}%)"
        delta_color_apl = "normal"
        delta_color_desert = "inverse"
    else:
        # Nationwide view: show historical evolution vs 2022 baseline
        if selected_year > 2022:
            delta_apl_val = avg_apl_filtered - base_2022["weighted_apl"]
            delta_desert_val = pct_desert_filtered - base_2022["pct_pop_in_desert"]
            pop_surge = desert_pop_filtered - base_2022["desert_pop"]
            delta_apl_str = f"{delta_apl_val:+.2f} vs 2022 baseline"
            delta_desert_str = f"{delta_desert_val:+.1f}% vs 2022 baseline"
            delta_pop_str = f"+{pop_surge/1e6:.2f}M citizens vs 2022"
            delta_cliff_str = f"{weighted_cliff_filtered - base_2022['retirement_cliff_pct']:+.1f}% vs 2022 baseline"
            delta_color_apl = "normal"
            delta_color_desert = "inverse"
        else:
            delta_apl_str = "National Reference Baseline"
            delta_desert_str = "National Reference (14.9%)"
            delta_pop_str = "100 Departments Monitored"
            delta_cliff_str = "Capacity held by GPs ≥ 60"
            delta_color_apl = "off"
            delta_color_desert = "off"

    # One-sentence headline insight
    st.info(
        f"**Headline Insight**: *In {selected_year}, the territorial gap remains wide: while national APL averages **{nat_base['weighted_apl']:.2f}**, the most critical departments plunge below **2.40**, trapping over **{desert_pop_filtered:,.0f} citizens** in care-deprived communes.*"
    )

    # Mandatory KPI Row with Deltas vs Baseline
    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        label="Average Primary Care Access",
        value=f"{avg_apl_filtered:.2f} APL",
        delta=delta_apl_str,
        delta_color=delta_color_apl,
        help="Weighted average consultations accessible per inhabitant per year.",
    )

    k2.metric(
        label="Pop. in Medical Deserts (APL < 2.5)",
        value=f"{pct_desert_filtered:.1f}%",
        delta=delta_desert_str,
        delta_color=delta_color_desert,
        help="Percentage of the population residing in communes below the DREES critical threshold (2.5).",
    )

    k3.metric(
        label="Affected Citizen Count",
        value=f"{desert_pop_filtered:,.0f}",
        delta=delta_pop_str,
        delta_color="off",
        help="Total population living under degraded access conditions.",
    )

    k4.metric(
        label="Retirement Cliff Exposure",
        value=f"{weighted_cliff_filtered:.1f}%",
        delta=delta_cliff_str,
        delta_color="off" if not has_region_filter and selected_year == 2022 else "inverse",
        help="Proportion of total primary care capacity provided by practitioners aged 60 and over.",
    )

    st.markdown("---")

    # Map Control & Rendering
    c_map, c_trend = st.columns([1.3, 1])

    with c_map:
        st.subheader("Interactive Choropleth Map (Metropolitan France)")
        map_metric = st.selectbox(
            "Select Map Metric Layer:",
            options=["weighted_apl", "pct_pop_in_desert", "delta_desert_pct_since_2022", "retirement_cliff_pct"],
            format_func=lambda x: {
                "weighted_apl": "Primary Care Access Index (APL)",
                "pct_pop_in_desert": "% Population in Medical Desert (< 2.5)",
                "delta_desert_pct_since_2022": "2-Year Shift: Desert Pop Surge (% pts vs 2022)",
                "retirement_cliff_pct": "Doctor Retirement Cliff (% Capacity by GPs ≥ 60)",
            }[x],
            help="Toggle layers to view overall accessibility, extreme deficits, recent 2-year shifts, or doctor age exposure.",
        )

        geojson = load_geojson()

        # When analyzing the 2-Year Shift, always benchmark the full 2022 -> 2024 trajectory
        if map_metric == "delta_desert_pct_since_2022":
            map_data = depts_df[depts_df["year"] == 2024].copy()
            if selected_regions:
                map_data = map_data[map_data["region_name"].isin(selected_regions)]
            st.info("*Displaying the 2-Year Shift (2022 → 2024): Cool Teal = Stable / Preserved | Deep Red = Severe Crisis.*")
        else:
            map_data = filtered_depts

        fig_map = plot_choropleth_map(map_data, geojson, metric=map_metric)
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(
            "**Analytical Takeaway**: *Why do regions like Brittany look stable? Coastal and western departments benefit from high practitioner attractiveness, masking acute degradation in outer suburban rings (e.g. Yvelines +22 pts, Essonne +19.6 pts) and rural basins.*"
        )

    with c_trend:
        st.subheader("Temporal Evolution (2022 - 2024)")
        st.markdown(
            "Track how departmental accessibility evolves against the **national benchmark** and the **critical threshold band**."
        )

        available_depts = sorted(filtered_depts["dept_name"].unique())
        default_depts = [d for d in ["Mayenne", "Indre", "Creuse", "Paris", "Rhône"] if d in available_depts]
        if not default_depts and available_depts:
            default_depts = available_depts[:3]

        selected_trend_depts = st.multiselect(
            "Compare Specific Departments:",
            options=available_depts,
            default=default_depts[:4],
            help="Select departments to compare their trajectories.",
        )

        fig_trend = plot_timeseries_evolution(depts_df, selected_trend_depts, nat_summary)
        st.plotly_chart(fig_trend, use_container_width=True)
