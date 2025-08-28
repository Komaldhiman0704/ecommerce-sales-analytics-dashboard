"""
E-Commerce Analytics Dashboard
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

# Basic page setup
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

# Simple, clean styling with left-aligned header
st.markdown("""
<style>
    .main-header {
        color: #2c3e50;
        font-size: 2.5rem;
        text-align: left;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .subtitle {
        color: #7f8c8d;
        font-size: 1.1rem;
        text-align: left;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .section-title {
        color: #34495e;
        font-size: 1.3rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        text-align: center;
        padding: 1rem;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Optimized data loading functions
@st.cache_data(ttl=7200, show_spinner=False)
def load_data():
    try:
        df = pd.read_csv('data/processed/cleaned_data.csv')
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        return df, True
    except FileNotFoundError:
        return create_sample_data(), False
    except Exception:
        return create_sample_data(), False

@st.cache_data(show_spinner=False)
def create_sample_data():
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
    
    # Pre-allocate arrays for faster data generation
    n_records = 1000
    date_array = np.random.choice(dates, n_records)
    invoice_array = [f'INV{i+1000:04d}' for i in range(n_records)]
    stock_codes = ['A001', 'A002', 'A003', 'A004', 'A005']
    products = [
        'Premium Coffee Mug', 'Wireless Headphones', 'Smartphone Case',
        'Bluetooth Speaker', 'USB Cable', 'Phone Charger'
    ]
    countries = ['United Kingdom', 'Germany', 'France', 'Spain']
    
    # Vectorized data generation
    data = {
        'InvoiceNo': invoice_array,
        'StockCode': np.random.choice(stock_codes, n_records),
        'Description': np.random.choice(products, n_records),
        'Quantity': np.random.randint(1, 10, n_records),
        'InvoiceDate': date_array,
        'UnitPrice': np.random.uniform(5.0, 50.0, n_records),
        'CustomerID': np.random.randint(1000, 1100, n_records),
        'Country': np.random.choice(countries, n_records)
    }
    
    df = pd.DataFrame(data)
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    return df

@st.cache_data(ttl=7200, show_spinner=False)
def load_customer_segments():
    try:
        return pd.read_csv('data/processed/customer_segments.csv')
    except FileNotFoundError:
        return None

# Cached calculation functions
@st.cache_data(show_spinner=False)
def calculate_metrics(filtered_df):
    """Pre-calculate all metrics for faster rendering"""
    total_revenue = filtered_df['TotalAmount'].sum()
    total_orders = filtered_df['InvoiceNo'].nunique()
    unique_customers = filtered_df['CustomerID'].nunique()
    avg_order_value = filtered_df.groupby('InvoiceNo')['TotalAmount'].sum().mean()
    return total_revenue, total_orders, unique_customers, avg_order_value

@st.cache_data(show_spinner=False)
def prepare_daily_sales(filtered_df):
    """Pre-calculate daily sales data"""
    daily_sales = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date).agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()
    daily_sales.columns = ['Date', 'Revenue', 'Orders']
    return daily_sales

@st.cache_data(show_spinner=False)
def prepare_country_data(filtered_df):
    """Pre-calculate country performance data"""
    country_sales = filtered_df.groupby('Country')['TotalAmount'].sum().reset_index()
    return country_sales.sort_values('TotalAmount', ascending=False)

@st.cache_data(show_spinner=False)
def prepare_product_data(filtered_df):
    """Pre-calculate product performance data"""
    if 'Description' not in filtered_df.columns:
        return None
    product_sales = filtered_df.groupby('Description')['TotalAmount'].sum().reset_index()
    return product_sales.sort_values('TotalAmount', ascending=False).head(5)

@st.cache_data(show_spinner=False)
def prepare_customer_metrics(filtered_df):
    """Pre-calculate customer metrics"""
    return filtered_df.groupby('CustomerID').agg({
        'TotalAmount': 'sum',
        'InvoiceNo': 'nunique'
    }).reset_index()

def main():
    # Left-aligned header for more natural look
    st.markdown('<h1 class="main-header">📊 E-Commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Business Performance & Customer Insights</p>', unsafe_allow_html=True)
    
    # Load data once
    df, data_loaded = load_data()
    customer_segments = load_customer_segments()
    
    # Simple sidebar filters
    st.sidebar.title("🎛️ Filters")
    
    # Date filter
    st.sidebar.subheader("Date Range")
    date_min = df['InvoiceDate'].min().date()
    date_max = df['InvoiceDate'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", value=date_min)
    end_date = st.sidebar.date_input("End Date", value=date_max)
    
    # Country filter
    st.sidebar.subheader("Country")
    countries = sorted(df['Country'].unique().tolist())
    selected_countries = st.sidebar.multiselect("Select Countries", countries, default=countries)
    
    # Product filter
    st.sidebar.subheader("Products")
    selected_products = []
    if 'Description' in df.columns:
        products = df['Description'].unique().tolist()
        selected_products = st.sidebar.multiselect("Select Products", products, default=products)
    
    # Apply filters efficiently using boolean indexing
    mask = (
        (df['InvoiceDate'].dt.date >= start_date) & 
        (df['InvoiceDate'].dt.date <= end_date) &
        (df['Country'].isin(selected_countries))
    )
    
    if selected_products:
        mask = mask & (df['Description'].isin(selected_products))
    
    filtered_df = df[mask]
    
    if filtered_df.empty:
        st.warning("⚠️ No data matches your selected filters.")
        return
    
    # Key Metrics - use cached calculations
    st.markdown('<h2 class="section-title">📈 Key Performance Metrics</h2>', unsafe_allow_html=True)
    
    total_revenue, total_orders, unique_customers, avg_order_value = calculate_metrics(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Revenue", f"£{total_revenue:,.0f}")
    with col2:
        st.metric("📦 Total Orders", f"{total_orders:,}")
    with col3:
        st.metric("👥 Unique Customers", f"{unique_customers:,}")
    with col4:
        st.metric("🛒 Avg Order Value", f"£{avg_order_value:.0f}")
    
    # Sales Trends - use cached data preparation
    st.markdown('<h2 class="section-title">📊 Sales Analysis</h2>', unsafe_allow_html=True)
    
    daily_sales = prepare_daily_sales(filtered_df)
    
    # Revenue trend chart
    fig_revenue = px.line(daily_sales, x='Date', y='Revenue', 
                         title='Daily Revenue Trend',
                         labels={'Revenue': 'Revenue (£)', 'Date': 'Date'})
    fig_revenue.update_traces(line_color='#3498db', line_width=2)
    fig_revenue.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Two column layout for additional charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Country performance - use cached data
        country_sales = prepare_country_data(filtered_df)
        
        fig_country = px.bar(country_sales, x='Country', y='TotalAmount',
                            title='Revenue by Country',
                            labels={'TotalAmount': 'Revenue (£)'})
        fig_country.update_traces(marker_color='#2ecc71')
        fig_country.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_country, use_container_width=True)
    
    with col2:
        # Top products - use cached data
        product_sales = prepare_product_data(filtered_df)
        if product_sales is not None:
            fig_products = px.bar(product_sales, x='TotalAmount', y='Description',
                                 title='Top 5 Products by Revenue',
                                 labels={'TotalAmount': 'Revenue (£)', 'Description': 'Product'},
                                 orientation='h')
            fig_products.update_traces(marker_color='#e74c3c')
            fig_products.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_products, use_container_width=True)
    
    # Customer Analysis
    st.markdown('<h2 class="section-title">👥 Customer Insights</h2>', unsafe_allow_html=True)
    
    if customer_segments is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer segments pie chart
            segment_counts = customer_segments['Customer_Segment'].value_counts()
            fig_segments = px.pie(values=segment_counts.values, names=segment_counts.index,
                                 title='Customer Segments Distribution')
            fig_segments.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_segments, use_container_width=True)
        
        with col2:
            # Customer metrics
            st.subheader("Customer Statistics")
            total_customers = len(customer_segments)
            st.write(f"**Total Customers:** {total_customers:,}")
            
            if 'Monetary' in customer_segments.columns:
                avg_customer_value = customer_segments['Monetary'].mean()
                st.write(f"**Average Customer Value:** £{avg_customer_value:.0f}")
                
                top_customers = customer_segments['Monetary'].quantile(0.8)
                st.write(f"**Top 20% Customer Value:** £{top_customers:.0f}")
    else:
        # Basic customer analysis from main data - use cached calculations
        customer_metrics = prepare_customer_metrics(filtered_df)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_customer_value = customer_metrics['TotalAmount'].mean()
            st.metric("💳 Avg Customer Value", f"£{avg_customer_value:.0f}")
        
        with col2:
            avg_orders_per_customer = customer_metrics['InvoiceNo'].mean()
            st.metric("📈 Avg Orders per Customer", f"{avg_orders_per_customer:.1f}")
        
        with col3:
            repeat_customers = (customer_metrics['InvoiceNo'] > 1).sum()
            repeat_rate = (repeat_customers / len(customer_metrics)) * 100
            st.metric("🔄 Repeat Customer Rate", f"{repeat_rate:.1f}%")
    
    # Data Summary
    st.markdown('<h2 class="section-title">📋 Data Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Data Range**")
        st.write(f"From: {start_date}")
        st.write(f"To: {end_date}")
        st.write(f"Days: {(end_date - start_date).days}")
    
    with col2:
        st.write("**Records**")
        st.write(f"Total Records: {len(filtered_df):,}")
        st.write(f"Countries: {len(selected_countries)}")
        st.write(f"Products: {filtered_df['Description'].nunique() if 'Description' in filtered_df.columns else 'N/A'}")
    
    with col3:
        st.write("**Performance**")
        best_day = daily_sales.loc[daily_sales['Revenue'].idxmax()]
        st.write(f"Best Day: {best_day['Date']}")
        st.write(f"Best Revenue: £{best_day['Revenue']:,.0f}")
        st.write(f"Avg Daily Revenue: £{daily_sales['Revenue'].mean():,.0f}")

if __name__ == "__main__":
    main()
