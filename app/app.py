
"""
E-Commerce Analytics Dashboard
=============================
Author: Komal
Date: August 2025
Dashboard for analyzing e-commerce sales and customer data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import warnings

warnings.filterwarnings('ignore')

# Page setup
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Compact styling with reduced white space
st.markdown("""
<style>
    /* Remove top padding and margins */
    .stMainBlockContainer {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 0rem;
    }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Reduce gaps between elements */
    .stVerticalBlock {
        gap: 0.2rem;
    }
    
    /* Compact header styling */
    .title {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 0.2rem;
        padding: 0;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin-bottom: 1rem;
        padding: 0;
    }
    
    /* Compact metric containers */
    div[data-testid="metric-container"] {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 0.8rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    
    /* Compact section headers */
    .section-header {
        background: #f1f3f4;
        padding: 8px 15px;
        border-radius: 5px;
        border-left: 3px solid #3498db;
        margin: 10px 0 8px 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Reduce sidebar padding */
    .css-1d391kg {
        padding-top: 1rem;
        padding-right: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
    }
    
    /* Compact tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 3px;
        margin-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 35px;
        padding: 0 12px;
        font-size: 0.9rem;
    }
    
    /* Reduce chart container padding */
    .stPlotlyChart {
        margin-bottom: 0.5rem;
    }
    
    /* Compact columns */
    .stColumn {
        padding: 0 0.3rem;
    }
    
    /* Reduce dataframe padding */
    .stDataFrame {
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit menu and footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Compact expander */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Load data functions
@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv('data/processed/cleaned_data.csv')
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        return df, True
    except FileNotFoundError:
        return create_sample_data(), False
    except Exception:
        return create_sample_data(), False

@st.cache_data
def create_sample_data():
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    
    data = []
    for i in range(1000):
        date = np.random.choice(dates)
        data.append({
            'InvoiceNo': f'INV{i+1000:04d}',
            'StockCode': np.random.choice(['A001', 'A002', 'A003', 'A004', 'A005']),
            'Description': np.random.choice([
                'Premium Coffee Mug', 'Wireless Headphones', 'Smartphone Case',
                'Bluetooth Speaker', 'USB Cable', 'Phone Charger'
            ]),
            'Quantity': np.random.randint(1, 10),
            'InvoiceDate': date,
            'UnitPrice': np.random.uniform(5.0, 50.0),
            'CustomerID': np.random.randint(1000, 1100),
            'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'Spain'])
        })
    
    df = pd.DataFrame(data)
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    return df

@st.cache_data(ttl=3600)
def load_customer_segments():
    try:
        return pd.read_csv('data/processed/customer_segments.csv')
    except FileNotFoundError:
        return None

def main():
    # Compact header
    st.markdown('<h1 class="title">E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Business Performance & Customer Insights</p>', unsafe_allow_html=True)
    
    # Load data
    df, data_loaded = load_data()
    customer_segments = load_customer_segments()
    
    # Compact sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
        # Date range - more compact
        st.markdown("**📊 Period**")
        date_min = df['InvoiceDate'].min().date()
        date_max = df['InvoiceDate'].max().date()
        
        start_date = st.date_input("From", value=date_min, min_value=date_min, max_value=date_max, key="start")
        end_date = st.date_input("To", value=date_max, min_value=date_min, max_value=date_max, key="end")
        
        # Geographic filter
        st.markdown("**🌍 Markets**")
        countries = sorted(df['Country'].unique().tolist())
        all_countries = st.checkbox("All Countries", value=True)
        
        if all_countries:
            selected_countries = countries
        else:
            selected_countries = st.multiselect("Select", countries, default=countries[:2])
        
        # Product filter
        st.markdown("**📦 Products**")
        if 'Description' in df.columns:
            top_products = df['Description'].value_counts().head(8).index.tolist()
            all_products = st.checkbox("All Products", value=True)
            
            if not all_products:
                selected_products = st.multiselect("Select", top_products, default=top_products[:2])
            else:
                selected_products = df['Description'].unique().tolist()
        else:
            selected_products = []
        
        if st.button("🔄 Refresh", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    # Apply filters
    filtered_df = df[
        (df['InvoiceDate'].dt.date >= start_date) & 
        (df['InvoiceDate'].dt.date <= end_date) &
        (df['Country'].isin(selected_countries))
    ]
    
    if not all_products and selected_products:
        filtered_df = filtered_df[filtered_df['Description'].isin(selected_products)]
    
    if filtered_df.empty:
        st.warning("No data matches your filters.")
        return
    
    # Compact KPIs
    st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = filtered_df['TotalAmount'].sum()
        st.metric("Revenue", f"£{total_revenue:,.0f}")
    
    with col2:
        total_orders = filtered_df['InvoiceNo'].nunique()
        st.metric("Orders", f"{total_orders:,}")
    
    with col3:
        unique_customers = filtered_df['CustomerID'].nunique()
        st.metric("Customers", f"{unique_customers:,}")
    
    with col4:
        avg_order_value = filtered_df.groupby('InvoiceNo')['TotalAmount'].sum().mean()
        st.metric("Avg Order", f"£{avg_order_value:.0f}")
    
    # Compact analytics
    st.markdown('<div class="section-header">📊 Analytics</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🗺️ Geography", "🛍️ Products"])
    
    with tab1:
        # Daily sales - more compact
        daily_sales = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date).agg({
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        daily_sales.columns = ['Date', 'Revenue', 'Orders']
        
        # Single revenue chart (more space efficient)
        fig_revenue = px.line(daily_sales, x='Date', y='Revenue', title='Daily Revenue')
        fig_revenue.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
        
        # Compact side-by-side metrics
        col1, col2 = st.columns(2)
        
        with col1:
            fig_orders = px.bar(daily_sales.tail(7), x='Date', y='Orders', title='Last 7 Days - Orders')
            fig_orders.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_orders, use_container_width=True)
        
        with col2:
            # Weekly summary
            weekly_avg = daily_sales['Revenue'].tail(7).mean()
            total_week = daily_sales['Revenue'].tail(7).sum()
            
            st.markdown("**📊 Weekly Summary**")
            st.write(f"**Total:** £{total_week:,.0f}")
            st.write(f"**Daily Avg:** £{weekly_avg:.0f}")
            st.write(f"**Best Day:** {daily_sales.tail(7).loc[daily_sales.tail(7)['Revenue'].idxmax(), 'Date']}")
    
    with tab2:
        country_sales = filtered_df.groupby('Country').agg({
            'TotalAmount': 'sum',
            'CustomerID': 'nunique'
        }).reset_index().sort_values('TotalAmount', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(country_sales, values='TotalAmount', names='Country', title='Revenue Share')
            fig_pie.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Compact country stats
            st.markdown("**🌍 Market Performance**")
            for i, row in country_sales.head(4).iterrows():
                pct = (row['TotalAmount'] / country_sales['TotalAmount'].sum()) * 100
                st.write(f"**{row['Country']}:** £{row['TotalAmount']:,.0f} ({pct:.1f}%)")
    
    with tab3:
        if 'Description' in filtered_df.columns:
            product_data = filtered_df.groupby('Description').agg({
                'TotalAmount': 'sum',
                'Quantity': 'sum'
            }).reset_index().sort_values('TotalAmount', ascending=False).head(8)
            
            # Compact product table
            st.markdown("**🏆 Top Products**")
            display_df = product_data.copy()
            display_df['Revenue'] = display_df['TotalAmount'].apply(lambda x: f"£{x:,.0f}")
            display_df['Units'] = display_df['Quantity'].apply(lambda x: f"{x:,}")
            
            # Show compact table
            st.dataframe(
                display_df[['Description', 'Revenue', 'Units']].head(6), 
                use_container_width=True, 
                hide_index=True,
                height=200
            )
    
    # Compact customer section
    st.markdown('<div class="section-header">👥 Customers</div>', unsafe_allow_html=True)
    
    if customer_segments is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            segment_counts = customer_segments['Customer_Segment'].value_counts()
            fig_segments = px.pie(values=segment_counts.values, names=segment_counts.index, title='Segments')
            fig_segments.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_segments, use_container_width=True)
        
        with col2:
            st.markdown("**📊 Customer Insights**")
            total_customers = len(customer_segments)
            champions = len(customer_segments[customer_segments['Customer_Segment'] == 'Champions']) if 'Champions' in customer_segments['Customer_Segment'].values else 0
            st.write(f"**Total Customers:** {total_customers:,}")
            st.write(f"**Champions:** {champions}")
            if 'Monetary' in customer_segments.columns:
                avg_value = customer_segments['Monetary'].mean()
                st.write(f"**Avg Customer Value:** £{avg_value:.0f}")
    else:
        customer_metrics = filtered_df.groupby('CustomerID').agg({
            'TotalAmount': 'sum',
            'InvoiceNo': 'nunique'
        }).reset_index()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Customer Value", f"£{customer_metrics['TotalAmount'].mean():.0f}")
        
        with col2:
            st.metric("Avg Orders/Customer", f"{customer_metrics['InvoiceNo'].mean():.1f}")
        
        with col3:
            repeat_rate = ((customer_metrics['InvoiceNo'] > 1).sum() / len(customer_metrics)) * 100
            st.metric("Repeat Rate", f"{repeat_rate:.1f}%")
    
    # Compact insights
    st.markdown('<div class="section-header">💡 Quick Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        daily_sales_calc = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date)['TotalAmount'].sum()
        peak_day = daily_sales_calc.idxmax()
        peak_revenue = daily_sales_calc.max()
        
        st.write(f"**🚀 Best Day:** {peak_day}")
        st.write(f"**💰 Peak Revenue:** £{peak_revenue:,.0f}")
        st.write(f"**📊 Analysis:** {len(daily_sales_calc)} days")
    
    with col2:
        avg_daily = daily_sales_calc.mean()
        country_sales_calc = filtered_df.groupby('Country')['TotalAmount'].sum()
        top_market = country_sales_calc.idxmax()
        
        st.write(f"**🎯 Daily Target:** £{avg_daily*1.1:.0f}")
        st.write(f"**🌍 Top Market:** {top_market}")
        st.write(f"**📈 Growth Opportunity:** Customer retention")
    
    # Compact footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption(f"**Data:** {len(filtered_df):,} records")
    
    with col2:
        st.caption(f"**Period:** {(end_date - start_date).days} days")
    
    with col3:
        st.caption(f"**Updated:** {datetime.now().strftime('%H:%M')}")

if __name__ == "__main__":
    main()
