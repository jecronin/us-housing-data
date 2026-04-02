import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# -- Page Configuration
st.set_page_config(page_title="Real Estate Insights", layout="wide")

# -- Constants (Realtor.com S3 Buckets)
URL_INV = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"
URL_HOT = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Hotness/RDC_Inventory_Hotness_Metrics_Zip_History.csv"

# -- Setup DuckDB for Remote Reading
@st.cache_resource
def get_connection():
    con = duckdb.connect(database=':memory:')
    # Install and load the httpfs extension to handle remote URLs efficiently
    con.execute("INSTALL httpfs; LOAD httpfs;")
    return con

@st.cache_data(ttl=86400)
def get_market_data(zip_code):
    con = get_connection()
    
    # We query the CSVs as 'external tables'
    # DuckDB will only fetch the bytes required for the filter
    query = f"""
    SELECT 
        CAST(inv.month_date_yyyymm AS VARCHAR) as date_str,
        inv.postal_code,
        inv.median_listing_price,
        inv.active_listing_count,
        inv.median_days_on_market,
        inv.new_listing_count,
        hot.hotness_rank
    FROM '{URL_INV}' AS inv
    INNER JOIN '{URL_HOT}' AS hot
        ON inv.postal_code = hot.postal_code 
        AND inv.month_date_yyyymm = hot.month_date_yyyymm
    WHERE inv.postal_code = '{zip_code}'
    ORDER BY inv.month_date_yyyymm ASC
    """
    return con.execute(query).df()

# -- UI Logic
st.title("🏡 Zip Code Market Pulse")

zip_input = st.text_input("Enter 5-Digit Zip Code:", value="43206", help="Type a zip and press Enter")

if zip_input:
    # Use a status container for better feedback during the 'stuck' phase
    with st.status(f"Scanning Realtor.com database for {zip_input}...", expanded=True) as status:
        try:
            df_tgt = get_market_data(zip_input)
            
            if df_tgt.empty:
                status.update(label="No data found.", state="error")
                st.warning(f"Zip code {zip_input} not found in the latest report.")
            else:
                status.update(label="Data retrieved!", state="complete", expanded=False)
                
                # Processing
                df_tgt['month_date_yyyymm'] = pd.to_datetime(df_tgt['date_str'], format='%Y%m')
                
                # Visualization
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(px.line(df_tgt, x='month_date_yyyymm', y='median_listing_price', title="Price Trend"), use_container_width=True)
                with col2:
                    st.plotly_chart(px.line(df_tgt, x='month_date_yyyymm', y='active_listing_count', title="Inventory Count"), use_container_width=True)
                
                st.dataframe(df_tgt, use_container_width=True)
        except Exception as e:
            status.update(label="Connection Error", state="error")
            st.error(f"The server timed out connecting to Realtor.com. Try refreshing. Error: {e}")
