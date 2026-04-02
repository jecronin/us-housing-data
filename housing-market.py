import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

# -- Page Configuration
st.set_page_config(page_title="Real Estate Insights", layout="wide")

# -- Constants & URLs
URL_INV = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"
URL_HOT = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Hotness/RDC_Inventory_Hotness_Metrics_Zip_History.csv"

# -- Performance Optimized Data Engine (DuckDB)
@st.cache_data(ttl=86400) # Cache results for 24 hours
def get_market_data(zip_code):
    """
    Uses DuckDB to query remote CSVs directly. 
    Only pulls rows for the specific ZIP, saving massive amounts of RAM.
    """
    # Initialize DuckDB connection
    con = duckdb.connect(database=':memory:')
    
    # SQL Query to join remote CSVs on the fly
    query = f"""
    SELECT 
        CAST(inv.month_date_yyyymm AS VARCHAR) as date_str,
        inv.postal_code,
        inv.median_listing_price,
        inv.active_listing_count,
        inv.median_days_on_market,
        inv.new_listing_count,
        inv.price_increased_count,
        inv.price_reduced_count,
        hot.hotness_rank,
        hot.hotness_score
    FROM read_csv_auto('{URL_INV}') AS inv
    INNER JOIN read_csv_auto('{URL_HOT}') AS hot
        ON inv.postal_code = hot.postal_code 
        AND inv.month_date_yyyymm = hot.month_date_yyyymm
    WHERE inv.postal_code = '{zip_code}'
    ORDER BY inv.month_date_yyyymm ASC
    """
    df = con.execute(query).df()
    
    # Formatting
    df['month_date_yyyymm'] = pd.to_datetime(df['date_str'], format='%Y%m')
    return df

# -- Sidebar / Header
st.title("🏡 Realtor.com Market Optimizer")
st.markdown("Querying live research data using **DuckDB** for high-speed analysis.")

with st.sidebar:
    st.header("Location Filter")
    # Using text_input to avoid loading 40k+ items into a dropdown (prevents UI lag)
    zip_input = st.text_input("Enter 5-Digit Zip Code:", value="43206")
    
    st.info("💡 **Pro Tip:** DuckDB is fetching only the rows for this ZIP from the cloud, keeping memory usage near zero.")

# -- Execution
if zip_input:
    with st.spinner(f"Querying data for {zip_input}..."):
        try:
            df_tgt = get_market_data(zip_input)
            
            if df_tgt.empty:
                st.error(f"No data found for ZIP {zip_input}. Please check the code and try again.")
                st.stop()
                
            # Vectorized Rolling Metrics
            metrics = ['median_listing_price', 'active_listing_count', 'median_days_on_market', 'hotness_rank']
            for m in metrics:
                df_tgt[f"{m}_rolling"] = df_tgt[m].rolling(window=6).mean()

            # -- Metrics Row
            curr = df_tgt.iloc[-1]
            prev = df_tgt.iloc[-2] if len(df_tgt) > 1 else curr
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Median Price", f"${curr['median_listing_price']:,.0f}", f"{((curr['median_listing_price']/prev['median_listing_price'])-1)*100:.1f}%")
            m2.metric("Active Listings", int(curr['active_listing_count']))
            m3.metric("Avg Days on Market", int(curr['median_days_on_market']))
            m4.metric("Hotness Rank", int(curr['hotness_rank']))

            # -- Charts
            st.divider()
            c1, c2 = st.columns(2)
            
            with c1:
                fig_price = px.line(df_tgt, x='month_date_yyyymm', y=['median_listing_price', 'median_listing_price_rolling'], 
                                   title="Median Listing Price (6mo Moving Avg)", template="plotly_white")
                st.plotly_chart(fig_price, use_container_width=True)
                
                fig_inv = px.bar(df_tgt, x='month_date_yyyymm', y='new_listing_count', 
                                title="Monthly New Listings", template="plotly_white")
                st.plotly_chart(fig_inv, use_container_width=True)

            with c2:
                fig_hot = px.line(df_tgt, x='month_date_yyyymm', y='hotness_rank', 
                                 title="Hotness Rank (Lower is Hotter)", template="plotly_white")
                fig_hot.update_yaxes(autorange="reversed")
                st.plotly_chart(fig_hot, use_container_width=True)
                
                fig_days = px.area(df_tgt, x='month_date_yyyymm', y='median_days_on_market', 
                                  title="Median Days on Market", template="plotly_white")
                st.plotly_chart(fig_days, use_container_width=True)

            with st.expander("View Raw Data Table"):
                st.dataframe(df_tgt, use_container_width=True)

        except Exception as e:
            st.error(f"Error fetching data: {e}")
