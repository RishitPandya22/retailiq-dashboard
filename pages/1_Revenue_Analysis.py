import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Revenue Analysis · RetailIQ",
    page_icon="💰",
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
    .page-header { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #58a6ff; border-radius: 10px; padding: 16px 24px; margin-bottom: 24px; }
    .page-header-title { font-size: 20px; font-weight: 600; color: #58a6ff; font-family: monospace; }
    .page-header-sub { font-size: 13px; color: #8b949e; margin-top: 4px; }
    .insight-box { background: #161b22; border: 1px solid #30363d; border-left: 3px solid #3fb950; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 13px; color: #8b949e; }
    .insight-box strong { color: #3fb950; }
</style>
"""

CHART_LAYOUT = dict(
    paper_bgcolor='#161b22', plot_bgcolor='#0d1117',
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
    df['MonthStr'] = df['InvoiceDate'].dt.strftime('%b %Y')
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df['InvoiceDate'].dt.hour
    df['Quarter'] = df['InvoiceDate'].dt.quarter
    return df

st.markdown(DARK_CSS, unsafe_allow_html=True)
with st.spinner('Loading data...'):
    df = load_data()

with st.sidebar:
    st.markdown('<div class="sidebar-title">RetailIQ Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)
    all_countries = sorted(df['Country'].unique().tolist())
    selected_countries = st.multiselect("Country", options=all_countries, default=all_countries)
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    granularity = st.selectbox("Chart Granularity", options=["Monthly", "Weekly", "Quarterly"], index=0)
    st.markdown("---")
    st.caption(f"🗓️ Data: {min_date.strftime('%b %Y')} → {max_date.strftime('%b %Y')}")
    st.caption("ℹ️ Dataset covers Dec 2010 – Dec 2011")

dff = df[df['Country'].isin(selected_countries)] if selected_countries else df.copy()
if len(date_range) == 2:
    dff = dff[(dff['InvoiceDate'].dt.date >= date_range[0]) & (dff['InvoiceDate'].dt.date <= date_range[1])]

st.markdown("""
<div class="page-header">
    <div class="page-header-title">💰 REVENUE ANALYSIS</div>
    <div class="page-header-sub">Trends · Seasonality · Day & Hour Patterns · Quarter Breakdown</div>
</div>
""", unsafe_allow_html=True)

total_rev = dff['Revenue'].sum()
avg_monthly = dff.groupby(dff['InvoiceDate'].dt.to_period('M'))['Revenue'].sum().mean()
best_month = dff.groupby('MonthStr')['Revenue'].sum().idxmax()
best_month_val = dff.groupby('MonthStr')['Revenue'].sum().max()
peak_day = dff.groupby('DayOfWeek')['Revenue'].sum().idxmax()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"${total_rev:,.0f}")
c2.metric("Avg Monthly Revenue", f"${avg_monthly:,.0f}")
c3.metric("Best Month", best_month, f"${best_month_val:,.0f}")
c4.metric("Peak Day", peak_day)

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("Revenue Trend")

if granularity == "Monthly":
    trend = dff.groupby(dff['InvoiceDate'].dt.to_period('M'))['Revenue'].sum().reset_index()
    trend['InvoiceDate'] = trend['InvoiceDate'].astype(str)
    x_col = 'InvoiceDate'
elif granularity == "Weekly":
    trend = dff.groupby(dff['InvoiceDate'].dt.to_period('W'))['Revenue'].sum().reset_index()
    trend['InvoiceDate'] = trend['InvoiceDate'].astype(str)
    x_col = 'InvoiceDate'
else:
    trend = dff.groupby('Quarter')['Revenue'].sum().reset_index()
    trend['Quarter'] = trend['Quarter'].apply(lambda x: f"Q{x}")
    x_col = 'Quarter'

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=trend[x_col], y=trend['Revenue'],
    mode='lines+markers',
    line=dict(color='#58a6ff', width=2.5),
    marker=dict(size=6, color='#58a6ff'),
    fill='tozeroy', fillcolor='rgba(88,166,255,0.07)',
))
fig_trend.update_layout(**CHART_LAYOUT, height=320, showlegend=False,
                        yaxis_tickprefix='$', yaxis_tickformat=',.0f')
st.plotly_chart(fig_trend, use_container_width=True)

monthly_rev = dff.groupby(dff['InvoiceDate'].dt.to_period('M'))['Revenue'].sum().reset_index()
monthly_rev.columns = ['Month', 'Revenue']
monthly_rev['MoM_Growth'] = monthly_rev['Revenue'].pct_change() * 100
monthly_rev['Month'] = monthly_rev['Month'].astype(str)

st.subheader("Month-over-Month Revenue Growth (%)")
colors = ['#3fb950' if v >= 0 else '#f85149' for v in monthly_rev['MoM_Growth'].fillna(0)]
fig_mom = go.Figure(go.Bar(
    x=monthly_rev['Month'], y=monthly_rev['MoM_Growth'].fillna(0),
    marker_color=colors, marker_line_width=0,
))
fig_mom.update_layout(**CHART_LAYOUT, height=260, showlegend=False, yaxis_ticksuffix='%')
fig_mom.add_hline(y=0, line_color='#30363d', line_width=1)
st.plotly_chart(fig_mom, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Revenue by Day of Week")
    dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    dow = dff.groupby('DayOfWeek')['Revenue'].sum().reindex(dow_order).reset_index()
    fig_dow = px.bar(dow, x='DayOfWeek', y='Revenue', color='Revenue',
                     color_continuous_scale=[[0,'#1f3a5f'],[1,'#58a6ff']])
    fig_dow.update_layout(**CHART_LAYOUT, height=280, coloraxis_showscale=False)
    fig_dow.update_traces(marker_line_width=0)
    st.plotly_chart(fig_dow, use_container_width=True)

with col2:
    st.subheader("Revenue by Hour of Day")
    hourly = dff.groupby('Hour')['Revenue'].sum().reset_index()
    fig_hour = px.bar(hourly, x='Hour', y='Revenue', color='Revenue',
                      color_continuous_scale=[[0,'#1a3a2a'],[1,'#3fb950']])
    fig_hour.update_layout(**CHART_LAYOUT, height=280, coloraxis_showscale=False)
    fig_hour.update_traces(marker_line_width=0)
    st.plotly_chart(fig_hour, use_container_width=True)

st.subheader("Quarterly Revenue Breakdown")
quarterly = dff.groupby('Quarter').agg(
    Revenue=('Revenue','sum'),
    Orders=('InvoiceNo','nunique'),
    Customers=('CustomerID','nunique')
).reset_index()
quarterly['Quarter'] = quarterly['Quarter'].apply(lambda x: f"Q{x}")
fig_q = px.bar(quarterly, x='Quarter', y='Revenue',
               color='Quarter',
               color_discrete_sequence=['#58a6ff','#3fb950','#f0883e','#bc8cff'],
               text=quarterly['Revenue'].apply(lambda x: f"${x:,.0f}"))
fig_q.update_traces(marker_line_width=0, textposition='outside', textfont=dict(color='#8b949e', size=11))
fig_q.update_layout(**CHART_LAYOUT, height=300, showlegend=False,
                    yaxis_tickprefix='$', yaxis_tickformat=',.0f')
st.plotly_chart(fig_q, use_container_width=True)

st.markdown("---")
st.subheader("Key Business Insights")
top_q = quarterly.loc[quarterly['Revenue'].idxmax(), 'Quarter']
top_hour = hourly.loc[hourly['Revenue'].idxmax(), 'Hour']
top_day = dow.loc[dow['Revenue'].idxmax(), 'DayOfWeek']
st.markdown(f"""
<div class="insight-box"><strong>Peak Quarter:</strong> {top_q} generates the most revenue — align promotions and inventory ahead of this period.</div>
<div class="insight-box"><strong>Best Day:</strong> {top_day} is the highest revenue day — ideal for launching flash sales or email campaigns.</div>
<div class="insight-box"><strong>Peak Hour:</strong> Most purchases happen around {top_hour}:00 — schedule marketing pushes 1 hour before this window.</div>
""", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<p style="text-align:center;color:#8b949e;font-size:12px;font-family:monospace;">RetailIQ Dashboard · Built by Rishit Pandya · University of Adelaide · 2025</p>', unsafe_allow_html=True)