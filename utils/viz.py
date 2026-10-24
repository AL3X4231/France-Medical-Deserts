"""
Visualization & Plotting Utilities
utils/viz.py - High-quality Plotly charts with threshold annotations and consistent themes
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.config import APL_CRITICAL_THRESHOLD, APL_NATIONAL_TARGET

# Professional styling palette
COLOR_CRITICAL = "#e63946"   # Crimson red for alert / desert
COLOR_WARNING = "#f4a261"    # Orange / Amber for moderate
COLOR_SAFE = "#2a9d8f"       # Teal green for satisfactory
COLOR_ACCENT = "#1d3557"     # Deep navy blue for headings / benchmarks
COLOR_BG_CARD = "#f8f9fa"

PLOTLY_TEMPLATE = "plotly_white"


def format_hover(label: str, val: float, unit: str = "") -> str:
    """Format numeric hover values gracefully."""
    return f"{label}: <b>{val:,.2f}{unit}</b>"


def plot_choropleth_map(depts_df: pd.DataFrame, geojson: dict, metric: str = "weighted_apl") -> go.Figure:
    """
    Generate an interactive Choropleth Map of France by Department.
    Supports metric toggle: APL, % population in desert, or Retirement Cliff %.
    """
    metric_configs = {
        "weighted_apl": {
            "title": "Primary Care Access Index (APL - Consultations/year/inhabitant)",
            "colorscale": "RdYlGn",
            "range": [2.0, 5.0],
            "unit": " consult./hab/yr",
            "reverse": False,
        },
        "pct_pop_in_desert": {
            "title": "% Population in Medical Desert (APL < 2.5)",
            "colorscale": "Reds",
            "range": [0, 60],
            "unit": " %",
            "reverse": False,
        },
        "retirement_cliff_pct": {
            "title": "Retirement Cliff: % GP Capacity Held by Doctors ≥ 60",
            "colorscale": "YlOrRd",
            "range": [15, 45],
            "unit": " %",
            "reverse": False,
        },
        "delta_desert_pct_since_2022": {
            "title": "2-Year Surge: Desert Pop % Change vs 2022 Baseline",
            "colorscale": [
                [0.0, "#2a9d8f"],   # Cool Teal for stable / preserved (Brittany, etc.)
                [0.2, "#e9c46a"],   # Amber for slight shift (+2% to +4%)
                [0.45, "#f4a261"],  # Orange for moderate (+6% to +9%)
                [0.7, "#e76f51"],   # Coral red for high (+10% to +14%)
                [1.0, "#b7094c"],   # Deep Crimson for catastrophic surge (> +18%)
            ],
            "range": [-3, 22],
            "unit": " % pts",
            "reverse": False,
        },
    }

    cfg = metric_configs.get(metric, metric_configs["weighted_apl"])

    # Filter to metropolitan France for the GeoJSON (departments with 2-char code or 2A/2B)
    metro_df = depts_df[depts_df["dept_code"].str.len() <= 2].copy()

    custom_data = [
        metro_df["dept_name"],
        metro_df["dept_code"],
        metro_df["region_name"],
        metro_df["weighted_apl"],
        metro_df["pct_pop_in_desert"],
        metro_df["desert_pop"],
        metro_df["retirement_cliff_pct"],
        metro_df["total_pop"],
        metro_df.get("delta_desert_pct_since_2022", pd.Series([0.0]*len(metro_df))),
    ]

    fig = go.Figure(
        go.Choropleth(
            geojson=geojson,
            locations=metro_df["dept_code"],
            z=metro_df[metric],
            featureidkey="properties.code",
            colorscale=cfg["colorscale"],
            zmin=cfg["range"][0],
            zmax=cfg["range"][1],
            reversescale=cfg["reverse"],
            marker_line_color="rgba(128, 128, 128, 0.4)",
            marker_line_width=0.6,
            customdata=list(zip(*custom_data)),
            hovertemplate=(
                "<b>%{customdata[0]} (%{customdata[1]})</b><br>"
                "Region: %{customdata[2]}<br>"
                "------------------------------------<br>"
                "• Mean APL: <b>%{customdata[3]:.2f}</b> consult./hab/yr<br>"
                "• Pop in Medical Desert: <b>%{customdata[4]:.1f}%</b> (%{customdata[5]:,d} hab.)<br>"
                "• 2-Year Desert Shift: <b>%{customdata[8]:+.1f}% pts</b> vs 2022<br>"
                "• Doctors ≥ 60 yrs old: <b>%{customdata[6]:.1f}%</b><br>"
                "• Total Population: %{customdata[7]:,d}<extra></extra>"
            ),
            colorbar=dict(
                title=dict(text=cfg["unit"].strip(), side="top"),
                thickness=15,
                len=0.75,
                x=0.98,
            ),
        )
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        showcountries=False,
        showcoastlines=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=520,
    )

    return fig


def plot_timeseries_evolution(depts_df: pd.DataFrame, selected_depts: list, nat_summary: dict) -> go.Figure:
    """
    Line chart showing APL evolution across years (2022-2024).
    Includes reference threshold band for critical level (2.5) and national average line.
    """
    fig = go.Figure()

    # Critical threshold reference line and band
    fig.add_hrect(
        y0=0,
        y1=APL_CRITICAL_THRESHOLD,
        fillcolor="rgba(230, 57, 70, 0.12)",
        line_width=0,
        annotation_text="Critical Care Deficit Zone (APL < 2.5)",
        annotation_position="bottom right",
        annotation_font=dict(color=COLOR_CRITICAL, size=11),
    )

    fig.add_hline(
        y=APL_CRITICAL_THRESHOLD,
        line_dash="dash",
        line_color=COLOR_CRITICAL,
        line_width=2,
    )

    # National average benchmark
    years = [2022, 2023, 2024]
    nat_apls = [nat_summary[str(y)]["weighted_apl"] for y in years]

    fig.add_trace(
        go.Scatter(
            x=years,
            y=nat_apls,
            mode="lines+markers",
            name="France National Average",
            line=dict(color="#1d3557", width=3, dash="dot"),
            marker=dict(size=8, symbol="diamond"),
            hovertemplate="National Average: <b>%{y:.2f}</b><extra></extra>",
        )
    )

    # Filtered departments
    colors = px.colors.qualitative.Bold
    for i, dept in enumerate(selected_depts):
        d_sub = depts_df[depts_df["dept_name"] == dept].sort_values("year")
        if not d_sub.empty:
            color = colors[i % len(colors)]
            fig.add_trace(
                go.Scatter(
                    x=d_sub["year"],
                    y=d_sub["weighted_apl"],
                    mode="lines+markers",
                    name=dept,
                    line=dict(width=2.5, color=color),
                    marker=dict(size=7),
                    hovertemplate=f"<b>{dept}</b> (%{{x}}): <b>%{{y:.2f}}</b> consult./hab/yr<extra></extra>",
                )
            )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="<b>Primary Care Trajectory (2022 - 2024) vs. Critical Threshold</b>",
        xaxis=dict(title="Year", tickvals=[2022, 2023, 2024], tickformat="d"),
        yaxis=dict(title="Weighted APL (Consultations / Inhabitant / Year)", range=[1.5, 5.0]),
        margin=dict(l=20, r=20, t=50, b=30),
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def plot_distribution_box(communes_df: pd.DataFrame, dept_name: str, year: int = 2024) -> go.Figure:
    """
    Boxplot of commune-level APL inside the selected department vs nationwide.
    Reveals intra-departmental inequality.
    """
    sub_dept = communes_df[(communes_df["dept_name"] == dept_name) & (communes_df["year"] == year)]
    sub_nat = communes_df[communes_df["year"] == year]

    fig = go.Figure()

    # National distribution
    fig.add_trace(
        go.Box(
            y=sub_nat["apl_all"],
            name="All France Communes",
            boxpoints=False,
            marker_color="#90be6d",
            line_color="#4d908e",
        )
    )

    # Department distribution with points
    fig.add_trace(
        go.Box(
            y=sub_dept["apl_all"],
            name=f"{dept_name} Communes",
            boxpoints="outliers",
            jitter=0.3,
            pointpos=-1.8,
            marker_color="#f94144",
            line_color="#d62828",
            customdata=sub_dept[["commune_name", "pop_total"]],
            hovertemplate="<b>%{customdata[0]}</b><br>APL: %{y:.2f}<br>Pop: %{customdata[1]:,d}<extra></extra>",
        )
    )

    # Critical threshold
    fig.add_hline(
        y=APL_CRITICAL_THRESHOLD,
        line_dash="dash",
        line_color=COLOR_CRITICAL,
        line_width=2,
        annotation_text="Critical Threshold (2.5)",
        annotation_position="bottom right",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"<b>Intra-Departmental Disparity: Commune APL in {dept_name} (Year {year})</b>",
        yaxis=dict(title="APL (Consultations / hab / yr)", range=[0, 8.0]),
        margin=dict(l=20, r=20, t=50, b=30),
        height=380,
    )

    return fig


def plot_correlation_scatter(depts_df: pd.DataFrame, year: int = 2024) -> go.Figure:
    """
    Scatter plot: X = Retirement Cliff (% GPs >= 60 yrs old), Y = Current Weighted APL.
    Bubble size = Total Population.
    Identifies high-risk departments in the bottom-right quadrant ("The Danger Zone").
    """
    sub = depts_df[depts_df["year"] == year].copy()

    # Categorize into quadrants
    med_cliff = sub["retirement_cliff_pct"].median()
    
    sub["quadrant"] = "Normal"
    danger_mask = (sub["weighted_apl"] < 3.2) & (sub["retirement_cliff_pct"] > med_cliff)
    sub.loc[danger_mask, "quadrant"] = "High Risk (Care Deficit + Aging Doctors)"

    fig = px.scatter(
        sub,
        x="retirement_cliff_pct",
        y="weighted_apl",
        size="total_pop",
        color="quadrant",
        color_discrete_map={
            "Normal": "#457b9d",
            "High Risk (Care Deficit + Aging Doctors)": "#e63946",
        },
        hover_name="dept_name",
        hover_data={
            "dept_code": True,
            "region_name": True,
            "weighted_apl": ":.2f",
            "retirement_cliff_pct": ":.1f",
            "pct_pop_in_desert": ":.1f",
            "total_pop": ":,",
            "quadrant": False,
        },
        labels={
            "retirement_cliff_pct": "GP Retirement Exposure (% Capacity Held by Doctors ≥ 60)",
            "weighted_apl": "Weighted Primary Care Access (APL)",
            "total_pop": "Population",
        },
        template=PLOTLY_TEMPLATE,
    )

    # Reference lines
    fig.add_hline(
        y=APL_CRITICAL_THRESHOLD,
        line_dash="dash",
        line_color=COLOR_CRITICAL,
        line_width=1.5,
        annotation_text="Critical Threshold (2.5)",
        annotation_position="bottom left",
    )
    fig.add_vline(
        x=med_cliff,
        line_dash="dot",
        line_color="#6c757d",
        line_width=1.5,
        annotation_text=f"Median Doctor Aging ({med_cliff:.1f}%)",
        annotation_position="top right",
    )

    fig.update_layout(
        title=f"<b>The Retirement Cliff vs. Current Care Access ({year})</b>",
        height=450,
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )

    return fig


def plot_small_multiples_regions(depts_df: pd.DataFrame, year: int = 2024) -> go.Figure:
    """
    Horizontal Bar Chart comparing the French administrative regions
    ranked by the percentage of their population trapped in medical deserts.
    """
    reg_group = depts_df[depts_df["year"] == year].groupby("region_name").agg({
        "total_pop": "sum",
        "desert_pop": "sum",
        "weighted_apl": "mean",
    }).reset_index()

    reg_group["pct_desert"] = (reg_group["desert_pop"] / reg_group["total_pop"] * 100.0).round(1)
    reg_group = reg_group.sort_values("pct_desert", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=reg_group["pct_desert"],
            y=reg_group["region_name"],
            orientation="h",
            marker=dict(
                color=reg_group["pct_desert"],
                colorscale="Reds",
                line=dict(color="#1d3557", width=0.5),
            ),
            customdata=list(zip(reg_group["desert_pop"], reg_group["total_pop"], reg_group["weighted_apl"])),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "• % Pop in Desert: <b>%{x:.1f}%</b><br>"
                "• Population Concerned: %{customdata[0]:,d} / %{customdata[1]:,d}<br>"
                "• Regional Avg APL: %{customdata[2]:.2f}<extra></extra>"
            ),
        )
    )

    # National average marker
    nat_pct = (reg_group["desert_pop"].sum() / reg_group["total_pop"].sum() * 100.0)
    fig.add_vline(
        x=nat_pct,
        line_dash="dash",
        line_color="#1d3557",
        line_width=2,
        annotation_text=f"National Avg: {nat_pct:.1f}%",
        annotation_position="bottom right",
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=f"<b>Regional Inequality: % Population Living in Medical Deserts ({year})</b>",
        xaxis=dict(title="% of Regional Population with APL < 2.5", range=[0, 40]),
        yaxis=dict(title=""),
        margin=dict(l=20, r=20, t=50, b=30),
        height=400,
    )

    return fig


from plotly.subplots import make_subplots


def plot_simulation_impact(baseline_desert_pop: int, simulated_desert_pop: int,
                           baseline_desert_communes: int, simulated_desert_communes: int) -> go.Figure:
    """
    Comparison chart for the What-If policy simulator:
    Uses dual subplots so that Population (millions) and Communes (thousands)
    each have an independent, beautifully scaled axis without squashing.
    """
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=[
            "<b>Population Trapped in Medical Deserts</b>",
            "<b>Number of Desert Municipalities (Communes)</b>",
        ],
        horizontal_spacing=0.15,
    )

    # Subplot 1: Population in Desert
    fig.add_trace(
        go.Bar(
            name="Current Situation",
            x=["Current", "Simulated"],
            y=[baseline_desert_pop, simulated_desert_pop],
            marker_color=[COLOR_CRITICAL, COLOR_SAFE],
            text=[f"{baseline_desert_pop / 1e6:.2f} M", f"{simulated_desert_pop / 1e6:.2f} M"],
            textposition="auto",
            hovertemplate="<b>%{x}</b>: %{y:,d} inhabitants<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=1,
    )

    # Subplot 2: Communes in Desert
    fig.add_trace(
        go.Bar(
            name="Desert Communes",
            x=["Current", "Simulated"],
            y=[baseline_desert_communes, simulated_desert_communes],
            marker_color=[COLOR_CRITICAL, COLOR_SAFE],
            text=[f"{baseline_desert_communes:,d}", f"{simulated_desert_communes:,d}"],
            textposition="auto",
            hovertemplate="<b>%{x}</b>: %{y:,d} communes<extra></extra>",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title="<b>Simulation Impact: Deficit Reduction Before vs. After Policy Intervention</b>",
        margin=dict(l=20, r=20, t=60, b=30),
        height=380,
    )

    fig.update_yaxes(title_text="Citizens (Inhabitants)", row=1, col=1)
    fig.update_yaxes(title_text="Municipalities (Count)", row=1, col=2)

    return fig
