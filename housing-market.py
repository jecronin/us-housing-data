import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# -- Page Configuration
st.set_page_config(page_title="ZIP Market Tracker", layout="wide")

# -- URL for Inventory Data Only
URL_INV = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"

@st.cache_resource
def get_connection():
    con = duckdb.connect(database=':memory:')
    con.execute("INSTALL httpfs; LOAD httpfs;")
    return con

@st.cache_data(ttl=86400)
def get_inventory_data(zip_code):
    con = get_connection()
    # Simple query: No join, much lower latency
    query = f"""
    SELECT 
        CAST(month_date_yyyymm AS VARCHAR) as date_str,
        postal_code,
        median_listing_price,
        active_listing_count,
        median_days_on_market,
        new_listing_count,
        price_increased_count,
        price_reduced_count
    FROM '{URL_INV}'
    WHERE postal_code = '{zip_code}'
    ORDER BY month_date_yyyymm ASC
    """
    return con.execute(query).df()

# -- UI
st.title("🏡 ZIP Code Inventory Tracker")
st.markdown("Direct-stream from Realtor.com Inventory Metrics.")

zip_input = st.text_input("Enter 5-Digit Zip Code:", value="43206")

if zip_input:
    with st.spinner(f"Fetching inventory for {zip_input}..."):
        try:
            df = get_inventory_data(zip_input)
            
            if df.empty:
                st.warning(f"No inventory records found for {zip_input}.")
            else:
                # Post-processing
                df['month_date_yyyymm'] = pd.to_datetime(df['date_str'], format='%Y%m')
                
                # KPIs
                curr = df.iloc[-1]
                prev = df.iloc[-2] if len(df) > 1 else curr
                
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Median Price", f"${curr['median_listing_price']:,.0f}", 
                           f"{((curr['median_listing_price']/prev['median_listing_price'])-1)*100:.1f}%")
                kpi2.metric("Active Listings", int(curr['active_listing_count']))
                kpi3.metric("New Listings (Mo)", int(curr['new_listing_count']))

                # Visuals
                st.divider()
                c1, c2 = st.columns(2)
                
                with c1:
                    # Price Trend with 6-month rolling average
                    df['price_rolling'] = df['median_listing_price'].rolling(6).mean()
                    fig1 = px.line(df, x='month_date_yyyymm', y=['median_listing_price', 'price_rolling'],
                                  title="Median Listing Price Evolution",
                                  labels={'value': 'Price ($)', 'month_date_yyyymm': 'Month'})
                    st.plotly_chart(fig1, use_container_width=True)

                with c2:
                    # Inventory breakdown
                    fig2 = px.bar(df, x='month_date_yyyymm', y=['active_listing_count', 'new_listing_count'],
                                 title="Inventory: Active vs New Listings",
                                 barmode='group')
                    st.plotly_chart(fig2, use_container_width=True)

                st.subheader("Historical Data Detail")
                st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Connection Error: {e}. The Realtor.com server might be busy.")
