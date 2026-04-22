import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Customer Analytics · RetailIQ",
    page_icon="👥",
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
    .page-header { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #3fb950; border-radius: 10px; padding: 16px 24px; margin-bottom: 24px; }
    .page-header-title { font-size: 20px; font-weight: 600; color: #3fb950; font-family: monospace; }
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
    df['CustomerID'] = df['CustomerID'].astype(int)
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
    top_n = st.slider("Top N Customers", min_value=5, max_value=30, value=10, step=5)
    st.markdown("---")
    st.caption(f"🗓️ Data: {min_date.strftime('%b %Y')} → {max_date.strftime('%b %Y')}")
    st.caption("ℹ️ Dataset covers Dec 2010 – Dec 2011")

dff = df[df['Country'].isin(selected_countries)] if selected_countries else df.copy()
if len(date_range) == 2:
    dff = dff[(dff['InvoiceDate'].dt.date >= date_range[0]) & (dff['InvoiceDate'].dt.date <= date_range[1])]

st.markdown("""
<div class="page-header">
    <div class="page-header-title">👥 CUSTOMER ANALYTICS</div>
    <div class="page-header-sub">Spend Distribution · Top Customers · Cohort Retention · Geographic Analysis</div>
</div>
""", unsafe_allow_html=True)

customer_summary = dff.groupby('CustomerID').agg(
    TotalRevenue=('Revenue','sum'),
    TotalOrders=('InvoiceNo','nunique'),
    TotalItems=('Quantity','sum'),
    FirstPurchase=('InvoiceDate','min'),
    LastPurchase=('InvoiceDate','max'),
).reset_index()
customer_summary['AvgOrderValue'] = customer_summary['TotalRevenue'] / customer_summary['TotalOrders']
customer_summary['CustomerLifespan'] = (customer_summary['LastPurchase'] - customer_summary['FirstPurchase']).dt.days

unique_customers = customer_summary['CustomerID'].nunique()
avg_spend = customer_summary['TotalRevenue'].mean()
avg_orders = customer_summary['TotalOrders'].mean()
repeat_customers = (customer_summary['TotalOrders'] > 1).sum()
repeat_rate = repeat_customers / unique_customers * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Unique Customers", f"{unique_customers:,}")
c2.metric("Avg Spend per Customer", f"${avg_spend:,.2f}")
c3.metric("Avg Orders per Customer", f"{avg_orders:.1f}")
c4.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Top {top_n} Customers by Revenue")
    top_customers = customer_summary.nlargest(top_n, 'TotalRevenue').copy()
    top_customers['CustomerID'] = top_customers['CustomerID'].astype(str)
    fig_top = px.bar(top_customers.sort_values('TotalRevenue'),
                     x='TotalRevenue', y='CustomerID', orientation='h',
                     color='TotalRevenue',
                     color_continuous_scale=[[0,'#1a3a2a'],[1,'#3fb950']])
    fig_top.update_layout(**CHART_LAYOUT, height=380, coloraxis_showscale=False,
                          xaxis_tickprefix='$', xaxis_tickformat=',.0f')
    fig_top.update_traces(marker_line_width=0)
    st.plotly_chart(fig_top, use_container_width=True)

with col2:
    st.subheader("Customer Spend Distribution")
    fig_hist = px.histogram(
        customer_summary[customer_summary['TotalRevenue'] < customer_summary['TotalRevenue'].quantile(0.95)],
        x='TotalRevenue', nbins=40, color_discrete_sequence=['#58a6ff']
    )
    fig_hist.update_layout(**CHART_LAYOUT, height=380,
                           xaxis_tickprefix='$', xaxis_tickformat=',.0f', showlegend=False)
    fig_hist.update_traces(marker_line_width=0)
    st.plotly_chart(fig_hist, use_container_width=True)

st.subheader("Cohort Retention Analysis")
st.caption("Each row = customers who made their first purchase in that month. Values show what % returned in subsequent months.")

dff_cohort = dff.copy()
dff_cohort['CohortMonth'] = dff_cohort.groupby('CustomerID')['InvoiceDate'].transform('min').dt.to_period('M')
dff_cohort['OrderMonth'] = dff_cohort['InvoiceDate'].dt.to_period('M')
dff_cohort['CohortIndex'] = (
    (dff_cohort['OrderMonth'].dt.year - dff_cohort['CohortMonth'].dt.year) * 12 +
    (dff_cohort['OrderMonth'].dt.month - dff_cohort['CohortMonth'].dt.month)
)
cohort_data = dff_cohort.groupby(['CohortMonth','CohortIndex'])['CustomerID'].nunique().reset_index()
cohort_pivot = cohort_data.pivot_table(index='CohortMonth', columns='CohortIndex', values='CustomerID')
cohort_pct = cohort_pivot.divide(cohort_pivot[0], axis=0) * 100
cohort_pct = cohort_pct.iloc[:, :7]
cohort_pct.index = cohort_pct.index.astype(str)

fig_cohort = go.Figure(data=go.Heatmap(
    z=cohort_pct.values,
    x=[f"Month {i}" for i in cohort_pct.columns],
    y=cohort_pct.index.tolist(),
    colorscale=[[0,'#0d1117'],[0.3,'#1f3a5f'],[0.7,'#1f6feb'],[1.0,'#58a6ff']],
    text=[[f"{v:.0f}%" if not pd.isna(v) else "" for v in row] for row in cohort_pct.values],
    texttemplate="%{text}",
    textfont=dict(size=11, color='#e6edf3'),
    showscale=True,
    colorbar=dict(tickfont=dict(color='#8b949e'), ticksuffix='%', bgcolor='#161b22', bordercolor='#30363d'),
))
fig_cohort.update_layout(
    **CHART_LAYOUT, height=420,
    xaxis=dict(side='top', gridcolor='#21262d', tickfont=dict(color='#8b949e')),
    yaxis=dict(autorange='reversed', gridcolor='#21262d', tickfont=dict(color='#8b949e')),
)
st.plotly_chart(fig_cohort, use_container_width=True)

st.subheader("Revenue by Country — World Map")
country_rev = dff.groupby('Country')['Revenue'].sum().reset_index()
fig_map = px.choropleth(country_rev, locations='Country', locationmode='country names',
                        color='Revenue',
                        color_continuous_scale=[[0,'#0d2b1a'],[0.3,'#0f6e56'],[1,'#3fb950']],
                        hover_name='Country', hover_data={'Revenue': ':$,.0f'})
fig_map.update_layout(
    paper_bgcolor='#161b22', font=dict(color='#8b949e', family='monospace'),
    geo=dict(bgcolor='#0d1117', landcolor='#21262d', oceancolor='#0d1117',
             showocean=True, lakecolor='#0d1117', countrycolor='#30363d',
             coastlinecolor='#30363d', showframe=False),
    coloraxis_colorbar=dict(tickfont=dict(color='#8b949e'), tickprefix='$', bgcolor='#161b22', bordercolor='#30363d'),
    margin=dict(l=0,r=0,t=20,b=0), height=420,
)
st.plotly_chart(fig_map, use_container_width=True)

st.subheader(f"Top {top_n} Customer Detail Table")
display_table = customer_summary.nlargest(top_n, 'TotalRevenue')[
    ['CustomerID','TotalRevenue','TotalOrders','AvgOrderValue','TotalItems','CustomerLifespan']
].copy()
display_table.columns = ['Customer ID','Total Revenue ($)','Total Orders','Avg Order Value ($)','Total Items','Lifespan (days)']
display_table['Total Revenue ($)'] = display_table['Total Revenue ($)'].apply(lambda x: f"${x:,.2f}")
display_table['Avg Order Value ($)'] = display_table['Avg Order Value ($)'].apply(lambda x: f"${x:,.2f}")
display_table['Customer ID'] = display_table['Customer ID'].astype(str)
st.dataframe(display_table, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Key Business Insights")
top_cust_rev = customer_summary.nlargest(1, 'TotalRevenue').iloc[0]
pct_80 = (customer_summary.nlargest(int(len(customer_summary) * 0.2), 'TotalRevenue')['TotalRevenue'].sum()
          / customer_summary['TotalRevenue'].sum() * 100)
st.markdown(f"""
<div class="insight-box"><strong>Top Customer:</strong> Customer {int(top_cust_rev['CustomerID'])} has spent ${top_cust_rev['TotalRevenue']:,.0f} across {int(top_cust_rev['TotalOrders'])} orders — prime candidate for a VIP loyalty programme.</div>
<div class="insight-box"><strong>Pareto Principle:</strong> The top 20% of customers account for {pct_80:.1f}% of total revenue — focus retention efforts on this segment.</div>
<div class="insight-box"><strong>Repeat Rate:</strong> {repeat_rate:.1f}% of customers made more than one purchase — improving this by 5% would significantly boost revenue.</div>
""", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<p style="text-align:center;color:#8b949e;font-size:12px;font-family:monospace;">RetailIQ Dashboard · Built by Rishit Pandya · University of Adelaide · 2025</p>', unsafe_allow_html=True)