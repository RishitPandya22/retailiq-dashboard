import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="RFM Segmentation · RetailIQ",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_CSS = """
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="metric-container"] { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; }
    [data-testid="metric-container"] label { color: #8b949e !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e6edf3 !important; font-family: monospace; font-size: 28px !important; }
    h1, h2, h3 { color: #e6edf3 !important; }
    .stSelectbox > div > div, .stMultiSelect > div > div { background-color: #161b22 !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
    hr { border-color: #30363d; }
    .sidebar-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #8b949e; margin-bottom: 8px; }
    .page-header { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #bc8cff; border-radius: 10px; padding: 16px 24px; margin-bottom: 24px; }
    .page-header-title { font-size: 20px; font-weight: 600; color: #bc8cff; font-family: monospace; }
    .page-header-sub { font-size: 13px; color: #8b949e; margin-top: 4px; }
    .seg-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .seg-title { font-size: 14px; font-weight: 600; font-family: monospace; }
    .seg-desc { font-size: 12px; color: #8b949e; margin-top: 4px; }
    .seg-stat { font-size: 13px; margin-top: 8px; }
    .insight-box { background: #161b22; border: 1px solid #30363d; border-left: 3px solid #bc8cff; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 13px; color: #8b949e; }
    .insight-box strong { color: #bc8cff; }
</style>
"""

CHART_LAYOUT = dict(
    paper_bgcolor='#161b22', plot_bgcolor='#0d1117',
    font=dict(color='#8b949e', family='monospace'),
    xaxis=dict(gridcolor='#21262d', linecolor='#30363d', tickfont=dict(color='#8b949e')),
    yaxis=dict(gridcolor='#21262d', linecolor='#30363d', tickfont=dict(color='#8b949e')),
    margin=dict(l=16, r=16, t=40, b=16),
)

SEGMENT_CONFIG = {
    'Champions':        {'color': '#3fb950', 'desc': 'Bought recently, buy often, spend the most'},
    'Loyal Customers':  {'color': '#58a6ff', 'desc': 'Buy regularly — reward them to keep them'},
    'Potential Loyalist':{'color': '#79c0ff','desc': 'Recent customers with decent frequency'},
    'Recent Customers': {'color': '#bc8cff', 'desc': 'Bought recently but not often yet'},
    'Promising':        {'color': '#d2a8ff', 'desc': 'Recent shoppers, low spend so far'},
    'Need Attention':   {'color': '#f0883e', 'desc': 'Above average but inactive lately'},
    'About to Sleep':   {'color': '#ffa657', 'desc': 'Below average — act before they churn'},
    'At Risk':          {'color': '#ff7b72', 'desc': 'Used to buy often — need re-engagement'},
    'Hibernating':      {'color': '#f85149', 'desc': 'Low value, infrequent, long gone'},
    'Lost':             {'color': '#8b949e', 'desc': 'Lowest scores — very hard to recover'},
}

@st.cache_data
def load_data():
    df = pd.read_excel('data/online_retail.xlsx', engine='openpyxl')
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=['CustomerID', 'InvoiceNo'])
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    df = df[df['Quantity'] > 0]
    df = df[df['UnitPrice'] > 0]
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['CustomerID'] = df['CustomerID'].astype(int)
    return df

@st.cache_data
def compute_rfm(df, country_list):
    dff = df[df['Country'].isin(country_list)] if country_list else df.copy()
    snapshot_date = dff['InvoiceDate'].max() + pd.Timedelta(days=1)
    rfm = dff.groupby('CustomerID').agg(
        Recency=('InvoiceDate', lambda x: (snapshot_date - x.max()).days),
        Frequency=('InvoiceNo', 'nunique'),
        Monetary=('Revenue', 'sum')
    ).reset_index()
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    rfm['RFM_Total'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']

    def segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'Recent Customers'
        elif r >= 4 and f >= 2:
            return 'Potential Loyalist'
        elif r >= 3 and f <= 2:
            return 'Promising'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Need Attention'
        elif r == 2 and f >= 2:
            return 'About to Sleep'
        elif r <= 2 and f >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2 and m <= 2:
            return 'Lost'
        else:
            return 'Hibernating'

    rfm['Segment'] = rfm.apply(segment, axis=1)
    return rfm

st.markdown(DARK_CSS, unsafe_allow_html=True)
with st.spinner('Loading data...'):
    df = load_data()

with st.sidebar:
    st.markdown('<div class="sidebar-title">RetailIQ Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)
    all_countries = sorted(df['Country'].unique().tolist())
    selected_countries = st.multiselect("Country", options=all_countries, default=all_countries)
    st.markdown("---")
    st.markdown('<div class="sidebar-title">What is RFM?</div>', unsafe_allow_html=True)
    st.caption("R = Recency: how recently they bought")
    st.caption("F = Frequency: how often they buy")
    st.caption("M = Monetary: how much they spend")
    st.caption("Each scored 1–5. Combined = customer segment.")
    st.markdown("---")
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    st.caption(f"🗓️ Data: {min_date.strftime('%b %Y')} → {max_date.strftime('%b %Y')}")

with st.spinner('Computing RFM scores...'):
    rfm = compute_rfm(df, selected_countries)

st.markdown("""
<div class="page-header">
    <div class="page-header-title">🧠 RFM SEGMENTATION</div>
    <div class="page-header-sub">Recency · Frequency · Monetary · Customer Segment Scoring</div>
</div>
""", unsafe_allow_html=True)

total_customers = len(rfm)
champions = len(rfm[rfm['Segment'] == 'Champions'])
at_risk = len(rfm[rfm['Segment'] == 'At Risk'])
lost = len(rfm[rfm['Segment'] == 'Lost'])
avg_monetary = rfm['Monetary'].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers Scored", f"{total_customers:,}")
c2.metric("Champions", f"{champions:,}", f"{champions/total_customers*100:.1f}% of base")
c3.metric("At Risk", f"{at_risk:,}", f"-{at_risk/total_customers*100:.1f}% needs action")
c4.metric("Avg Customer Value", f"${avg_monetary:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Segment Distribution ──────────────────────────────────
seg_summary = rfm.groupby('Segment').agg(
    Customers=('CustomerID','count'),
    Avg_Recency=('Recency','mean'),
    Avg_Frequency=('Frequency','mean'),
    Avg_Monetary=('Monetary','mean'),
    Total_Revenue=('Monetary','sum'),
).reset_index().sort_values('Total_Revenue', ascending=False)
seg_summary['Color'] = seg_summary['Segment'].map(lambda x: SEGMENT_CONFIG.get(x, {}).get('color', '#8b949e'))

col1, col2 = st.columns(2)

with col1:
    st.subheader("Customers per Segment")
    fig_seg = px.bar(
        seg_summary.sort_values('Customers'),
        x='Customers', y='Segment', orientation='h',
        color='Segment',
        color_discrete_map={s: SEGMENT_CONFIG[s]['color'] for s in SEGMENT_CONFIG},
    )
    fig_seg.update_layout(**CHART_LAYOUT, height=400, showlegend=False, yaxis_title='')
    fig_seg.update_traces(marker_line_width=0)
    st.plotly_chart(fig_seg, use_container_width=True)

with col2:
    st.subheader("Revenue per Segment")
    fig_rev = px.pie(
        seg_summary, values='Total_Revenue', names='Segment',
        color='Segment',
        color_discrete_map={s: SEGMENT_CONFIG[s]['color'] for s in SEGMENT_CONFIG},
        hole=0.5,
    )
    fig_rev.update_layout(
        paper_bgcolor='#161b22',
        font=dict(color='#8b949e', family='monospace'),
        legend=dict(font=dict(color='#8b949e'), bgcolor='#161b22'),
        margin=dict(l=16,r=16,t=40,b=16),
        height=400,
    )
    fig_rev.update_traces(textfont=dict(color='#e6edf3'))
    st.plotly_chart(fig_rev, use_container_width=True)

# ── RFM 3D Scatter ────────────────────────────────────────
st.subheader("RFM 3D Scatter — Recency vs Frequency vs Monetary")
st.caption("Each dot is a customer. Drag to rotate. Champions should cluster top-right with high monetary.")
sample = rfm.sample(min(1000, len(rfm)), random_state=42)
fig_3d = px.scatter_3d(
    sample, x='Recency', y='Frequency', z='Monetary',
    color='Segment',
    color_discrete_map={s: SEGMENT_CONFIG[s]['color'] for s in SEGMENT_CONFIG},
    hover_data=['CustomerID','RFM_Score'],
    opacity=0.75,
    size_max=6,
)
fig_3d.update_traces(marker=dict(size=3))
fig_3d.update_layout(
    paper_bgcolor='#161b22',
    scene=dict(
        bgcolor='#0d1117',
        xaxis=dict(backgroundcolor='#0d1117', gridcolor='#21262d', color='#8b949e'),
        yaxis=dict(backgroundcolor='#0d1117', gridcolor='#21262d', color='#8b949e'),
        zaxis=dict(backgroundcolor='#0d1117', gridcolor='#21262d', color='#8b949e'),
    ),
    font=dict(color='#8b949e', family='monospace'),
    legend=dict(font=dict(color='#8b949e'), bgcolor='#161b22'),
    margin=dict(l=0,r=0,t=40,b=0),
    height=500,
)
st.plotly_chart(fig_3d, use_container_width=True)

# ── Segment Deep Dive ─────────────────────────────────────
st.subheader("Segment Summary Table")
display_seg = seg_summary.copy()
display_seg['Avg_Recency'] = display_seg['Avg_Recency'].apply(lambda x: f"{x:.0f} days")
display_seg['Avg_Frequency'] = display_seg['Avg_Frequency'].apply(lambda x: f"{x:.1f} orders")
display_seg['Avg_Monetary'] = display_seg['Avg_Monetary'].apply(lambda x: f"${x:,.0f}")
display_seg['Total_Revenue'] = display_seg['Total_Revenue'].apply(lambda x: f"${x:,.0f}")
display_seg = display_seg.drop(columns=['Color'])
display_seg.columns = ['Segment','Customers','Avg Recency','Avg Frequency','Avg Spend','Total Revenue']
st.dataframe(display_seg, use_container_width=True, hide_index=True)

# ── Download ──────────────────────────────────────────────
st.subheader("Export Segmented Customer List")
st.caption("Download the full RFM-scored customer list as a CSV — ready for CRM or marketing automation import.")
export_df = rfm[['CustomerID','Recency','Frequency','Monetary','R_Score','F_Score','M_Score','RFM_Score','Segment']].copy()
export_df.columns = ['Customer ID','Recency (days)','Frequency (orders)','Monetary ($)','R Score','F Score','M Score','RFM Code','Segment']
csv = export_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="⬇️ Download RFM Customer Segments (CSV)",
    data=csv,
    file_name='rfm_segments_retailiq.csv',
    mime='text/csv',
)

st.markdown("---")
st.subheader("Key Business Insights")
top_seg = seg_summary.iloc[0]
champ_rev_pct = rfm[rfm['Segment']=='Champions']['Monetary'].sum() / rfm['Monetary'].sum() * 100
st.markdown(f"""
<div class="insight-box"><strong>Champions Revenue Share:</strong> {champions} Champion customers ({champions/total_customers*100:.1f}% of base) drive {champ_rev_pct:.1f}% of total revenue — protect this segment at all costs.</div>
<div class="insight-box"><strong>At Risk Alert:</strong> {at_risk} customers are At Risk — they used to buy regularly but haven't recently. A targeted win-back campaign (discount + personalised email) could recover significant revenue.</div>
<div class="insight-box"><strong>Growth Opportunity:</strong> Focus on converting "Potential Loyalists" and "Promising" customers into Loyal Customers — they're already engaged and just need the right nudge.</div>
""", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<p style="text-align:center;color:#8b949e;font-size:12px;font-family:monospace;">RetailIQ Dashboard · Built by Rishit Pandya · University of Adelaide · 2025</p>', unsafe_allow_html=True)