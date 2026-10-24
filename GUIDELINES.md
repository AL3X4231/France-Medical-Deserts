# EFREI Data Stories 2026 - Guidelines & Project Specifications
**Course**: Individual Student Project: Streamlit Dashboard  
**Instructor**: Mano Joseph Mathew (mano.mathew@efrei.fr)  
**Hashtags**: #EFREIDataStories2026 #EFREIParis #DataVisualization #Streamlit #DataStorytelling #OpenData  
**Target Submission Format**: `StApp26_<ID>_<NOM>_<GROUPE>.zip` (ex: `StApp26_20000_NOM_DAI.zip`)

---

## 1. Project Overview & Storytelling Arc
Build a reproducible data-storytelling web application using Streamlit that guides the user through a clear narrative:
$$\text{Problem / Hook} \longrightarrow \text{Analysis / Overview} \longrightarrow \text{Deep-Dives / Insights} \longrightarrow \text{Implications / What-If}$$

### Narrative Patterns (Choose one or combine sensibly):
- **Before / After change over time** (e.g. air quality before/after ZFE, energy transition).
- **Compare groups / regions** with a map and small multiples.
- **Rankings & distribution** (top/bottom N, inequality, outliers, uncertainty).
- **Flow / throughput** (Sankey, network, pipeline stages).
- **What-if exploration** (scenario sliders based on documented assumptions).

### Core Narrative Components:
1. **Hook**: Why this matters, audience definition, problem framing.
2. **Context & Overview**: Baseline KPIs, high-level trends.
3. **Key Insights**: Non-obvious patterns, distributions, drill-downs with 1-sentence headline insights.
4. **Implications & Next Steps**: Actionable takeaways, policy/business recommendations, scenario simulation.

---

## 2. Approved Data Portals
Must use **one dataset or a coherent bundle from one source**:
- **data.gouv.fr**: https://www.data.gouv.fr/datasets
- **Green Data for Health (GD4H)**: https://gd4h.ecologie.gouv.fr/en/catalogue
- **data.europa.eu**: https://data.europa.eu/data/combined?locale=en

*Criteria*: Reasonable size (local caching/parquet), clear question, rich temporal and geographical granularity, clean metadata and open license.

---

## 3. Mandatory Technical Requirements

### Stack & Compatibility:
- **Streamlit $\ge$ 1.33**
- Key libraries: `pandas`, `numpy`, `pyarrow`, `plotly`, `altair`, `geopandas` / `pydeck`, `requests`.

### Minimum Features Required:
- [x] **Sidebar controls**: filters, date range, region/entity, metric selection.
- [x] **$\ge$ 3 interactive visuals**: line charts, bar charts, map with tooltips/hover.
- [x] **At least one interactive map** (Choropleth / GeoJSON / Pydeck / Folium) if geo fields exist.
- [x] **Metrics header (KPIs)**: with $\Delta$ vs baseline tied to active filters.
- [x] **Data Quality & Caveats section**: missingness, duplicates, validation checks, collection biases.
- [x] **Performance**: `@st.cache_data(show_spinner=False)`, efficient merges, pre-aggregation.
- [x] **Accessibility & Visual rules**:
  - One-sentence **headline insight** per section.
  - Reference lines / bands for thresholds (e.g. OMS thresholds, legal limits).
  - Explicit labels on axes, units, legends, and data source captions.
  - High-contrast, accessible color palettes.
  - Help tooltips (`help="..."`).
- [x] **Data Ethics & Limitations**: privacy protection (aggregation), uncertainty discussion, avoid claiming false causality.

---

## 4. Recommended Code Architecture

```
project_root/
├── app.py                   # Main entry point (config, layout, navigation)
├── sections/
│   ├── intro.py             # Hook, context, problem framing, data caveats
│   ├── overview.py          # KPIs, macro trends, temporal changes
│   ├── deep_dives.py        # Regional comparisons, distributions, correlations
│   └── conclusions.py       # Actionable insights, what-if simulator, next steps
├── utils/
│   ├── io.py                # Data downloading, cached loading, license info
│   ├── prep.py              # Cleaning, normalization, feature engineering
│   └── viz.py               # Standardized Plotly/Altair charts & map builders
├── data/                    # Cleaned/processed parquet or cached data
├── assets/                  # Images, logos, documentation
├── requirements.txt         # Pinned dependencies
└── README.md                # Problem statement, execution guide, data dictionary
```

---

## 5. Evaluation Rubric (100 Points)

| Criteria | Points | Key Success Factors |
| :--- | :---: | :--- |
| **Narrative & Problem Framing** | **25 pts** | Clear audience, focused questions, strong hook, storyboard continuity, clear takeaways. |
| **Data Work** | **25 pts** | Proper cleaning, handling missing/duplicate data, validation, smart feature engineering (rates, per capita, deltas). |
| **Visualization & UX** | **25 pts** | Appropriate charts, annotations & thresholds, no clutter, clean colors, interactive tooltips, seamless UX. |
| **Engineering Quality** | **15 pts** | Modular structure (`sections/`, `utils/`), `@st.cache_data`, fast loading, clean code, `requirements.txt`. |
| **Communication** | **10 pts** | Clear report / README, transparent limitations & ethics, concise demo video (2–4 minutes). |

---

## 6. Deliverables Checklist
1. **Streamlit App**: fully functional, fast, deployable (Streamlit Community Cloud).
2. **Demo Video (2–4 minutes)**: walkthrough of narrative, interactions, and insights.
3. **Repository / Codebase**: clean git repo, structured modules, documented functions.
4. **README.md**: complete project documentation, deployment link, data sources, setup instructions.
5. **Zip Archive**: `StApp26_<ID>_<NOM>_<GROUPE>.zip` containing code, README, data scripts/links.
