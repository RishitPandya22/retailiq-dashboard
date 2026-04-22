# 📊 RetailIQ Dashboard

> **E-Commerce Sales Intelligence Platform** built on 400K+ real transactions
> RFM Segmentation · Cohort Analysis · Revenue Analytics · Product Intelligence

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://retailiq-dashboard-rp.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-FF4B4B?logo=streamlit&logoColor=white)

---

## 🚀 Live Demo

### 👉 [retailiq-dashboard-rp.streamlit.app](https://retailiq-dashboard-rp.streamlit.app/)

---

## 🔍 What Is This?

RetailIQ is a full-stack **business intelligence dashboard** that replicates the kind of analytics tooling used by real retail and e-commerce companies. It goes beyond basic charts — every page auto-generates actionable business insights from the filtered data, the way a real data analyst would present findings to stakeholders.

Built on the **UCI Online Retail Dataset** — 541,909 real transactions from a UK-based e-commerce retailer across 38 countries (Dec 2010 – Dec 2011).

---

## 🧭 Dashboard Pages

### `1` 📈 Overview
Global KPI cards, revenue over time, orders by day of week, top 10 countries by revenue, and a live country breakdown table. All metrics update in real time as you filter by country or date.

### `2` 💰 Revenue Analysis
Monthly / weekly / quarterly revenue trends, Month-over-Month growth bars (green = growth, red = decline), revenue by hour of day, revenue by day of week, and quarterly breakdown with auto-generated business insights.

### `3` 👥 Customer Analytics
- **Cohort Retention Heatmap** — tracks what % of customers return each month after their first purchase
- Top N customers by revenue with a lifespan metric
- Customer spend distribution histogram
- Interactive world map (choropleth) showing revenue by country
- Pareto principle insight (top 20% customer revenue share)

### `4` 🛍️ Product Intelligence
Top products by revenue vs volume (side-by-side), Revenue vs Units Sold bubble scatter, unit price distribution, most-returned products analysis, and a full searchable product table.

### `5` 🧠 RFM Segmentation *(Crown Jewel)*
Every customer is scored across three dimensions and placed into one of 10 segments:

| Dimension | What It Measures |
|-----------|-----------------|
| **R — Recency** | How recently did they buy? |
| **F — Frequency** | How often do they buy? |
| **M — Monetary** | How much do they spend? |

| Segment | Strategy |
|---------|----------|
| 🏆 Champions | Reward & upsell — your best customers |
| 💙 Loyal Customers | Enrol in loyalty programme |
| 🌱 Potential Loyalist | Nurture with targeted campaigns |
| 🆕 Recent Customers | Strong onboarding sequence |
| 🔶 About to Sleep | Time-sensitive re-engagement offer |
| ⚠️ At Risk | Win-back campaign — act now |
| 💤 Hibernating | Low-cost reactivation attempt |
| ❌ Lost | Write off or mass discount promo |

Includes a **3D interactive scatter plot** (Recency × Frequency × Monetary) and a **downloadable CSV** of all customers with RFM scores — ready for CRM or marketing automation import.

---

## 🛠️ Tech Stack

| Tool | Role |
|------|------|
| Python 3.13 | Core language |
| Pandas | Data cleaning, transformation, aggregation |
| NumPy | Numerical scoring (RFM quantiles) |
| Plotly | All interactive charts — line, bar, scatter, 3D, choropleth, heatmap, donut |
| Streamlit | Web app framework + cloud deployment |
| OpenPyXL | Excel file ingestion |

---

## 📁 Project Structure

```
retailiq-dashboard/
│
├── data/
│   └── online_retail.xlsx           # UCI Online Retail Dataset
│
├── pages/
│   ├── 1_Revenue_Analysis.py        # Revenue trends & patterns
│   ├── 2_Customer_Analytics.py      # Cohort analysis & customer metrics
│   ├── 3_Product_Intelligence.py    # Product performance & returns
│   └── 4_RFM_Segmentation.py        # RFM scoring & customer segments
│
├── app.py                           # Home overview dashboard
├── requirements.txt                 # Python dependencies
└── README.md                        # You are here
```

---

## ⚙️ Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/RishitPandya22/retailiq-dashboard.git
cd retailiq-dashboard

# 2. Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add the dataset
# Download from: https://archive.ics.uci.edu/dataset/352/online+retail
# Rename to online_retail.xlsx and place in the data/ folder

# 5. Run
streamlit run app.py
```

---

## 💡 Sample Insights This Dashboard Surfaces

- **Nov 2011** was the peak revenue month — driven by pre-Christmas wholesale ordering
- **Thursdays** generate the highest revenue — optimal day for email campaigns and flash sales
- **Top 20% of customers** account for ~80% of revenue (Pareto principle confirmed on real data)
- **962 Champion customers** drive 65%+ of total revenue despite being 22% of the base
- **201 At-Risk customers** represent a significant win-back opportunity
- **8,905 return transactions** flagged for product quality investigation

---

## 👨‍💻 Author

**Rishit Pandya**
Master of Data Science · University of Adelaide, South Australia 🇦🇺

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rishit%20Pandya-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rishit-pandya-854b7928a)
[![GitHub](https://img.shields.io/badge/GitHub-RishitPandya22-181717?logo=github&logoColor=white)](https://github.com/RishitPandya22)
[![Live App](https://img.shields.io/badge/Live%20App-RetailIQ-FF4B4B?logo=streamlit&logoColor=white)](https://retailiq-dashboard-rp.streamlit.app/)

---

## 📄 Dataset Credit

[UCI Online Retail Dataset](https://archive.ics.uci.edu/dataset/352/online+retail) — publicly available for research and educational use.
Chen, D., Sain, S.L., and Guo, K. (2012). Data mining for the online retail industry.