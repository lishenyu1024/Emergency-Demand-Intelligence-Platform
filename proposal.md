# ProjectName
FlightPath Optimizer

# Story
We are prototyping a sophisticated predictive analytics platform that will empower LifeFlight to strategically **forecast emergency medical demand** over a 5-10 year horizon and model **optimal resource allocation scenarios** (such as new base locations) to save more lives and ensure equitable service coverage.

# Stakeholder
Dan Koloski (Initial Contact), LifeFlight Staff (Eventual Users)

---

# Team
## Members
- [Shenyu Li] (Team Lead)
- [Yantong Guo]

## Repo
https://github.com/nudataviz/project-fall25-lishenyu1024

## Repo access
✅ Team lead is working with the instructor to ensure all members have access via GitHub Classroom team management.

---

# Data
## Describe
We will use historical and current **LifeFlight operational data** (including transport volume, patient origin/destination, asset utilization) combined with **external factors** (weather, hospital closures, demographic shifts) to train predictive models and execute scenario simulations.

## Link / Risks
The core data is currently available in a **SharePoint** repository accessible via Dan Koloski. The primary risk is the **complexity of integrating and synthesizing diverse external datasets** (e.g., population projections, weather data) required for accurate long-term **5-10 year forecasting** and variable 'what-if' modeling.

---

# Scope & Objectives (mapped to client request)
- **Predictive analytics**
  - 5–10 year demand forecasting using historical patterns and demographic trends
  - Integration of external factors (weather patterns, population changes, hospital closures)
  - Variable adjustment capabilities (assets, geographic coverage, shifting demand)
  - Scenario comparison tools for evaluating multiple strategic options
- **Resource optimization**
  - Current capacity vs. demand analysis
  - Base location optimization (e.g., Aroostook County evaluation)
  - Unmet demand identification and quantification
  - Asset utilization metrics and recommendations
- **Interactive dashboard & reporting**
  - Real-time scenario-modeling interface
  - Customizable inputs with immediate output updates
  - Executive-ready visuals for fundraising and board presentations
  - Export capabilities for strategic planning documentation
  - Explore existing research and methods (Jo Røislien’s research, NZ/AU examples)
  - Define key performance indicators and success metrics

---

# Visualization Plan (by category)
**Total: 5 categories, 19 core visuals** for a convincing prototype that can scale to production dashboards.

## 1) Demand Forecasting (4 charts)

### 1.1 Long-term Demand Forecast Line with Uncertainty Band (5–10 years)
- **Why (original requirement):**
  - “**5–10 year demand forecasting** using historical patterns and demographic trends”
  - “**Integration of external factors** (weather patterns, population changes, etc.)”
- **How (implementation suggestion):**
  - Model: hierarchical time series (Prophet/ARIMA with holidays/seasonality) or gradient boosting (LightGBM) with time-aware features.
  - Exogenous variables: population projections, age structure, seasonal indices, extreme-weather days, hospital change indicators.
  - Viz: annual/quarterly line with **95% confidence band**; level toggle (system/state/county/base).
  - Interaction: scenario switcher (baseline/optimistic/conservative external factors).

### 1.2 Seasonality & Day-of-Week/Hour Heatmap
- **Why (original requirement):** “**Analyze historical and current operational data** to predict future demand patterns”; “**Seasonal patterns**.”
- **How:** aggregate deployments to (month × weekday × hour); heatmap intensity = average missions per 1,000 population. Year filter, location switch, YoY/MoM deltas.

### 1.3 Demographics vs. Demand Elasticity (Scatter + Fit / Marginal Effects)
- **Why (original requirement):** “**Demographic shifts** and **evaluate service expansion scenarios**.”
- **How:** county-level regressions of missions per 1,000 vs. growth rate, 65+ share, disease burden; show elasticity coefficients with CIs and marginal impact bars by cohort (geriatrics/pediatrics/trauma).

### 1.4 External Event Impact Replay (Event Study Line + Structural Breaks)
- **Why (original requirement):** “**External factors** (hospital closures, population shifts)” and “**service area changes**.”
- **How:** causal impact via breakpoint regression / synthetic control / Bayesian structural time series; visualize pre/post with effect intervals and cumulative impact; event picker (e.g., a hospital closure).

---

## 2) Scenario Modeling (4 charts)

### 2.1 What-If Scenario Panel (Inputs → KPI Mini-Multiples)
- **Why:** “**Model ‘what-if’ scenarios** (resource allocation, new bases, service area changes)” and “**real-time scenario planning**.”
- **How:** sidebar parameters (fleet, crews, base locations, service radius, SLA target); main panel shows KPIs (missions, SLA attainment, unmet demand, cost) as mini-cards; save/compare scenarios.

### 2.2 Base Siting Coverage Map (Isochrones/Voronoi + Response Time)
- **Why:** “**Base location optimization** (e.g., Aroostook County).”
- **How:** drive-/flight-time isochrones + Voronoi; grid simulation of 5–20-minute coverage; heatmap coverage before/after candidate base; on-click updates SLA lift and incremental cost.

### 2.3 Service Area Sensitivity (Coverage vs. Response Time Pareto)
- **Why:** “**Compare multiple strategic options** under resource and geography changes.”
- **How:** plot Pareto frontier across radius/SLA thresholds; highlight chosen scenario and dominated options; allow weight sliders (population/SLA/cost) to auto-select an efficient point.

### 2.4 Weather-Driven Risk Boxes (Extreme Weather Frequency vs. Demand)
- **Why:** “**Integration of weather patterns**.”
- **How:** stratify by quantiles of extreme-weather days; boxplots of mission distribution; guides contingency staffing/aircraft redundancy policies.

---

## 3) Resource Optimization (5 charts)

### 3.1 Capacity vs. Demand Match (Stacked Area/Waterfall)
- **Why:** “**Current capacity vs. demand analysis**.”
- **How:** compute max serviceable missions by shift/aircraft/base; overlay demand curve and **highlight gaps** by time/region.

### 3.2 Fleet & Crew Utilization (Heatmap/Gantt)
- **Why:** “**Asset utilization metrics and recommendations**.”
- **How:** utilization, turnaround, standby, maintenance share; Gantt + utilization heatmap to expose bottleneck shifts/bases.

### 3.3 Unmet Demand Map + Quantification Bars
- **Why:** “**Unmet demand identification and quantification**.”
- **How:** estimate via SLA threshold breaches, failed dispatches, diversions; choropleth + Top-N bar chart with **opportunity gain** estimates.

### 3.4 Response-Time Distribution & SLA Attainment Curve
- **Why:** supports “**strategic decisions**” and “**real-time scenario planning**.”
- **How:** P(X ≤ SLA) curves with median/95th; facets by time-of-day/weather.

### 3.5 Marginal Benefit of Resource Increments (Prioritization Bars)
- **Why:** “**Asset allocation recommendations** and **scenario comparison**.”
- **How:** simulate incremental add-one (1 aircraft / 1 crew / 1 base) and show ΔKPI; rank by benefit-cost ratio.

---

## 4) KPI & Executive Dashboard (4 charts)

### 4.1 Core KPI Bullet Charts (Board Summary)
- **Why:** “**Executive-ready visualizations for fundraising and board presentations**”; “**KPIs & success metrics**.”
- **How:** missions, SLA, unmet demand, transfer success rate, flight hours, unit cost; bullet charts vs target/historic trend.

### 4.2 Trend Wall (Metric Cards + Lines)
- **Why:** “**Real-time scenario planning & strategic decision-making**.”
- **How:** KPI cards (YTD, YoY); monthly lines with short forecast tails.

### 4.3 Cost–Benefit–Throughput Dual-Axis
- **Why:** “**Strategic planning & fundraising** narrative.”
- **How:** unit service cost vs. social benefit / revenue; annotate key inflection points and scenario labels.

### 4.4 Safety & Quality SPC Control Charts
- **Why:** “**Define success metrics** including safety/quality.”
- **How:** incident rates with mean/UCL/LCL; call out assignable-cause points.

---

## 5) Reporting & Export (2 modules)

### 5.1 Scenario Comparison Table (Exportable)
- **Why:** “**Compare multiple strategic options**” and “**export capabilities**.”
- **How:** standardized KPI columns for scenarios A/B/C; one-click export to PDF/PPT.

### 5.2 Decision Path Sankey (Narrative)
- **Why:** “**Board/fundraising presentations**.”
- **How:** visualize “Objectives → Constraints → Alternatives → Selected Option” to make trade-offs explicit.

---

# Technical Approach

## Methods & Prior Art
- Align variable definitions and metric conventions with **Dan Koloski’s prior methodology/deliverables** to maintain comparability.
- Incorporate proven techniques from **Jo Røislien’s research** and **NZ/AU** aeromedical examples (seasonality, spatial coverage, response time).

## Modeling & Data Stack
- **Modeling:** Python (Prophet/ARIMA, LightGBM, Bayesian structural time series), causal impact methods; OR-Tools for location optimization.
- **GIS:** GeoPandas / OSMnx for isochrones and coverage modeling.
- **Visualization/App:** Streamlit or Observable for rapid prototyping; Power BI/Tableau for executive-grade dashboards and exports.
- **Data:** Operational logs (missions, timestamps, origins/destinations), fleet/crew rosters, maintenance, hospital events; external population forecasts, weather histories and projections.

## Interaction & Governance
- Centralize all scenario parameters in a **config table**; define KPIs as reusable measures/functions shared by models and dashboards; maintain scenario versions for A/B/C comparisons.

---

# KPIs & Success Metrics
- Missions (total / per 1,000 pop), SLA attainment (median/95th response time), Unmet demand, Transfer success rate, Flight hours, Fleet/Crew utilization, Unit cost, Safety/quality incident rates.

---

# Summary of Visuals
- **Demand Forecasting:** 4
- **Scenario Modeling:** 4
- **Resource Optimization:** 5
- **KPI & Executive Dashboard:** 4
- **Reporting & Export:** 2  
**Total:** **19 visuals**

---