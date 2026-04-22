import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Product Intelligence · RetailIQ",
    page_icon="🛍️",
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
    .page-header { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f0883e; border-radius: 10px; padding: 16px 24px; margin-bottom: 24px; }
    .page-header-title { font-size: 20px; font-weight: 600; color: #f0883e; font-family: monospace; }
    .page-header-sub { font-size: 13px; color: #8b949e; margin-top: 4px; }
    .insight-box { background: #161b22; border: 1px solid #30363d; border-left: 3px solid #f0883e; border-radius: 8px; padding: 12px 16px; margin: 8px 0; font-size: 13px; color: #8b949e; }
    .insight-box strong { color: #f0883e; }
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
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['IsReturn'] = df['InvoiceNo'].astype(str).str.startswith('C')
    df_clean = df[~df['IsReturn'] & (df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
    df_returns = df[df['IsReturn']].copy()
    return df_clean, df_returns

st.markdown(DARK_CSS, unsafe_allow_html=True)
with st.spinner('Loading data...'):
    df, df_returns = load_data()

with st.sidebar:
    st.markdown('<div class="sidebar-title">RetailIQ Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="sidebar-title">Filters</div>', unsafe_allow_html=True)
    all_countries = sorted(df['Country'].unique().tolist())
    selected_countries = st.multiselect("Country", options=all_countries, default=all_countries)
    min_date = df['InvoiceDate'].min().date()
    max_date = df['InvoiceDate'].max().date()
    date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    top_n = st.slider("Top N Products", min_value=5, max_value=25, value=10, step=5)
    st.markdown("---")
    st.caption(f"🗓️ Data: {min_date.strftime('%b %Y')} → {max_date.strftime('%b %Y')}")
    st.caption("ℹ️ Dataset covers Dec 2010 – Dec 2011")

dff = df[df['Country'].isin(selected_countries)] if selected_countries else df.copy()
if len(date_range) == 2:
    dff = dff[(dff['InvoiceDate'].dt.date >= date_range[0]) & (dff['InvoiceDate'].dt.date <= date_range[1])]

st.markdown("""
<div class="page-header">
    <div class="page-header-title">🛍️ PRODUCT INTELLIGENCE</div>
    <div class="page-header-sub">Top Products · Revenue vs Volume · Price Distribution · Returns Analysis</div>
</div>
""", unsafe_allow_html=True)

total_products = dff['StockCode'].nunique()
total_revenue = dff['Revenue'].sum()
avg_unit_price = dff['UnitPrice'].mean()
total_units_sold = dff['Quantity'].sum()
return_count = len(df_returns)
return_rate = return_count / (len(dff) + return_count) * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("Unique Products", f"{total_products:,}")
c2.metric("Total Units Sold", f"{total_units_sold:,}")
c3.metric("Avg Unit Price", f"${avg_unit_price:,.2f}")
c4.metric("Return Transactions", f"{return_count:,}", f"-{return_rate:.1f}% rate")

st.markdown("<br>", unsafe_allow_html=True)

product_summary = dff.groupby(['StockCode','Description']).agg(
    TotalRevenue=('Revenue','sum'),
    TotalQuantity=('Quantity','sum'),
    AvgPrice=('UnitPrice','mean'),
    OrderCount=('InvoiceNo','nunique'),
).reset_index().sort_values('TotalRevenue', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Top {top_n} Products by Revenue")
    top_rev = product_summary.head(top_n).copy()
    top_rev['Label'] = top_rev['Description'].str[:30]
    fig_rev = px.bar(top_rev.sort_values('TotalRevenue'),
                     x='TotalRevenue', y='Label', orientation='h',
                     color='TotalRevenue',
                     color_continuous_scale=[[0,'#2a1a0d'],[1,'#f0883e']])
    fig_rev.update_layout(**CHART_LAYOUT, height=400, coloraxis_showscale=False,
                          xaxis_tickprefix='$', xaxis_tickformat=',.0f', yaxis_title='')
    fig_rev.update_traces(marker_line_width=0)
    st.plotly_chart(fig_rev, use_container_width=True)

with col2:
    st.subheader(f"Top {top_n} Products by Volume Sold")
    top_qty = product_summary.nlargest(top_n, 'TotalQuantity').copy()
    top_qty['Label'] = top_qty['Description'].str[:30]
    fig_qty = px.bar(top_qty.sort_values('TotalQuantity'),
                     x='TotalQuantity', y='Label', orientation='h',
                     color='TotalQuantity',
                     color_continuous_scale=[[0,'#1f3a5f'],[1,'#58a6ff']])
    fig_qty.update_layout(**CHART_LAYOUT, height=400, coloraxis_showscale=False,
                          xaxis_tickformat=',.0f', yaxis_title='')
    fig_qty.update_traces(marker_line_width=0)
    st.plotly_chart(fig_qty, use_container_width=True)

st.subheader("Revenue vs Units Sold — Product Scatter")
st.caption("Bubble size = number of orders. Products in top-right are your star performers.")
scatter_data = product_summary.head(50).copy()
scatter_data['Label'] = scatter_data['Description'].str[:25]
fig_scatter = px.scatter(
    scatter_data, x='TotalQuantity', y='TotalRevenue',
    size='OrderCount', color='AvgPrice',
    hover_name='Label',
    color_continuous_scale=[[0,'#1a3a2a'],[0.5,'#3fb950'],[1,'#58a6ff']],
    size_max=40,
)
fig_scatter.update_layout(**CHART_LAYOUT, height=400,
                          xaxis_title='Total Units Sold', yaxis_title='Total Revenue ($)',
                          yaxis_tickprefix='$', yaxis_tickformat=',.0f',
                          coloraxis_colorbar=dict(title='Avg Price', tickfont=dict(color='#8b949e')))
fig_scatter.update_traces(marker=dict(line=dict(width=0)))
st.plotly_chart(fig_scatter, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Unit Price Distribution")
    price_data = dff[dff['UnitPrice'] < dff['UnitPrice'].quantile(0.95)]
    fig_price = px.histogram(price_data, x='UnitPrice', nbins=50,
                             color_discrete_sequence=['#bc8cff'])
    fig_price.update_layout(**CHART_LAYOUT, height=300,
                            xaxis_tickprefix='$', showlegend=False,
                            xaxis_title='Unit Price', yaxis_title='Count')
    fig_price.update_traces(marker_line_width=0)
    st.plotly_chart(fig_price, use_container_width=True)

with col4:
    st.subheader("Top Returned Products")
    if len(df_returns) > 0:
        returns_summary = df_returns.groupby('Description')['Quantity'].sum().abs().sort_values(ascending=False).head(10).reset_index()
        returns_summary.columns = ['Product', 'Return Qty']
        fig_ret = px.bar(returns_summary.sort_values('Return Qty'),
                         x='Return Qty', y='Product', orientation='h',
                         color='Return Qty',
                         color_continuous_scale=[[0,'#3a1a1a'],[1,'#f85149']])
        fig_ret.update_layout(**CHART_LAYOUT, height=300, coloraxis_showscale=False, yaxis_title='')
        fig_ret.update_traces(marker_line_width=0)
        st.plotly_chart(fig_ret, use_container_width=True)
    else:
        st.info("No return data for selected filters.")

st.subheader("Full Product Table")
display_prod = product_summary.head(50).copy()
display_prod['TotalRevenue'] = display_prod['TotalRevenue'].apply(lambda x: f"${x:,.2f}")
display_prod['AvgPrice'] = display_prod['AvgPrice'].apply(lambda x: f"${x:,.2f}")
display_prod['TotalQuantity'] = display_prod['TotalQuantity'].apply(lambda x: f"{x:,}")
display_prod = display_prod[['StockCode','Description','TotalRevenue','TotalQuantity','AvgPrice','OrderCount']]
display_prod.columns = ['Stock Code','Product','Revenue','Units Sold','Avg Price','Orders']
st.dataframe(display_prod, use_container_width=True, hide_index=True)

st.markdown("---")
st.subheader("Key Business Insights")
top_prod = product_summary.iloc[0]
high_vol_low_rev = product_summary.nlargest(20,'TotalQuantity').nsmallest(5,'TotalRevenue').iloc[0]
st.markdown(f"""
<div class="insight-box"><strong>Star Product:</strong> "{top_prod['Description'][:40]}" drives the most revenue at ${top_prod['TotalRevenue']:,.0f} — ensure it's always in stock.</div>
<div class="insight-box"><strong>High Volume, Low Revenue:</strong> "{high_vol_low_rev['Description'][:40]}" sells {high_vol_low_rev['TotalQuantity']:,.0f} units but low revenue — consider a price review.</div>
<div class="insight-box"><strong>Returns Alert:</strong> {return_count:,} return transactions detected ({return_rate:.1f}% of all transactions) — investigate top returned products for quality issues.</div>
""", unsafe_allow_html=True)
st.markdown("---")
st.markdown('<p style="text-align:center;color:#8b949e;font-size:12px;font-family:monospace;">RetailIQ Dashboard · Built by Rishit Pandya · University of Adelaide · 2025</p>', unsafe_allow_html=True)