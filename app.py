import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="RetailIQ Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

DARK_CSS = """
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    section[data-testid="stSidebar"] * { color: #e6edf3 !important; }
    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
    }
    [data-testid="metric-container"] label { color: #8b949e !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] { color: #e6edf3 !important; font-family: monospace; font-size: 28px !important; }
    [data-testid="stMetricDelta"] { font-size: 13px !important; }
    .js-plotly-plot { border-radius: 10px; }
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        color: #e6edf3 !important;
    }
    hr { border-color: #30363d; }
    h1, h2, h3 { color: #e6edf3 !important; }
    .sidebar-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #8b949e; margin-bottom: 8px; }
    .top-banner {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 24px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .banner-title { font-size: 22px; font-weight: 600; color: #58a6ff; font-family: monospace; letter-spacing: 1px; }
    .banner-sub { font-size: 13px; color: #8b949e; margin-top: 4px; }
    .banner-badge {
        background: #3fb95022;
        color: #3fb950;
        border: 1px solid #3fb95055;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        font-family: monospace;
    }
    .insight-box {
        background: #161b22;
        border: 1px solid #30363d;
        border-left: 3px solid #3fb950;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 13px;
        color: #8b949e;
    }
    .insight-box strong { color: #3fb950; }
</style>
"""

CHART_LAYOUT = dict(
    paper_bgcolor='#161b22',
    plot_bgcolor='#0d1117',
    font=dict(color='#8b949e', family='monospace'),
    xaxis=dict(gridcolor='#21262d', linecolor='#30363d', tickfont=dict(color='#8b949e')),
    yaxis=dict(gridcolor='#21262d', linecolor='#30363d', tickfont=dict(color='#8b949e')),
    margin=dict(l=16, r=16, t=40, b=16),
)

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
    df['Year'] = df['InvoiceDate'].dt.year
    df['Month'] = df['InvoiceDate'].dt.month
    df['MonthName'] = df['InvoiceDate'].dt.strftime('%b %Y')
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df['InvoiceDate'].dt.hour
    return df

st.markdown(DARK_CSS, unsafe_allow_html=True)

with st.spinner('Loading RetailIQ...'):
    df = load_data()

# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">RetailIQ Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)

    all_countries = sorted(df['Country'].unique().tolist())
    selected_countries = st.multiselect(
        "Country",
        options=all_countries,
        default=all_countries,
        help="Select one or more countries"
    )

    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-title">Dataset Info</div>', unsafe_allow_html=True)
    st.caption(f"📦 {len(df):,} transactions")
    st.caption(f"👥 {df['CustomerID'].nunique():,} customers")
    st.caption(f"🛍️ {df['StockCode'].nunique():,} products")
    st.caption(f"🗓️ Data: {min_date.strftime('%b %Y')} → {max_date.strftime('%b %Y')}")
    st.markdown("---")
    st.caption("ℹ️ This dataset covers Dec 2010 – Dec 2011 (real historical retail data)")

# ── Filter ───────────────────────────────────────────────
dff = df[df['Country'].isin(selected_countries)] if selected_countries else df.copy()
if len(date_range) == 2:
    dff = dff[
        (dff['InvoiceDate'].dt.date >= date_range[0]) &
        (dff['InvoiceDate'].dt.date <= date_range[1])
    ]

# ── Banner ───────────────────────────────────────────────
st.markdown(f"""
<div class="top-banner">
    <div>
        <div class="banner-title">📊 RETAILIQ DASHBOARD</div>
        <div class="banner-sub">E-Commerce Sales Intelligence · UK Online Retail Dataset · Dec 2010 – Dec 2011</div>
    </div>
    <div class="banner-badge">LIVE · {len(dff):,} records</div>
</div>
""", unsafe_allow_html=True)

# ── KPI Cards ────────────────────────────────────────────
total_revenue = dff['Revenue'].sum()
total_orders = dff['InvoiceNo'].nunique()
avg_order_value = dff.groupby('InvoiceNo')['Revenue'].sum().mean()
unique_customers = dff['CustomerID'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("Unique Customers", f"{unique_customers:,}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Revenue Over Time ────────────────────────────────────
st.subheader("Revenue Over Time")
monthly = (
    dff.groupby(dff['InvoiceDate'].dt.to_period('M'))['Revenue']
    .sum().reset_index()
)
monthly['InvoiceDate'] = monthly['InvoiceDate'].astype(str)

fig_rev = go.Figure()
fig_rev.add_trace(go.Scatter(
    x=monthly['InvoiceDate'],
    y=monthly['Revenue'],
    mode='lines+markers',
    line=dict(color='#58a6ff', width=2),
    marker=dict(size=5, color='#58a6ff'),
    fill='tozeroy',
    fillcolor='rgba(88,166,255,0.08)',
))
fig_rev.update_layout(
    **CHART_LAYOUT, height=300, showlegend=False,
    yaxis_tickprefix='$', yaxis_tickformat=',.0f',
)
st.plotly_chart(fig_rev, use_container_width=True)

# ── Bottom Row ───────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Orders by Day of Week")
    dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    dow = dff.groupby('DayOfWeek')['InvoiceNo'].nunique().reindex(dow_order).reset_index()
    dow.columns = ['Day', 'Orders']
    fig_dow = px.bar(dow, x='Day', y='Orders', color='Orders',
                     color_continuous_scale=[[0,'#1f3a5f'],[1,'#58a6ff']])
    fig_dow.update_layout(**CHART_LAYOUT, height=280, coloraxis_showscale=False)
    fig_dow.update_traces(marker_line_width=0)
    st.plotly_chart(fig_dow, use_container_width=True)

with col_b:
    st.subheader("Top 10 Countries by Revenue")
    top_countries = (
        dff.groupby('Country')['Revenue']
        .sum().sort_values(ascending=True).tail(10).reset_index()
    )
    fig_ctry = px.bar(top_countries, x='Revenue', y='Country', orientation='h',
                      color='Revenue', color_continuous_scale=[[0,'#1a3a2a'],[1,'#3fb950']])
    fig_ctry.update_layout(**CHART_LAYOUT, height=280, coloraxis_showscale=False)
    fig_ctry.update_traces(marker_line_width=0)
    st.plotly_chart(fig_ctry, use_container_width=True)

# ── Country Breakdown ─────────────────────────────────────
st.subheader("Revenue Breakdown by Country")
country_rev = dff.groupby('Country').agg(
    Revenue=('Revenue','sum'),
    Orders=('InvoiceNo','nunique'),
    Customers=('CustomerID','nunique')
).reset_index().sort_values('Revenue', ascending=False).head(20)
country_rev['Avg Order Value'] = country_rev['Revenue'] / country_rev['Orders']
country_rev['Revenue'] = country_rev['Revenue'].apply(lambda x: f"${x:,.0f}")
country_rev['Avg Order Value'] = country_rev['Avg Order Value'].apply(lambda x: f"${x:,.2f}")
st.dataframe(country_rev, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#8b949e;font-size:12px;font-family:monospace;">'
    'RetailIQ Dashboard · Built by Rishit Pandya · University of Adelaide · 2025'
    '</p>',
    unsafe_allow_html=True
)