#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import geocoder

st.set_page_config(layout="wide")

# -- Read in the data
url = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"
url_hot = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Hotness/RDC_Inventory_Hotness_Metrics_Zip_History.csv"
cols = ['month_date_yyyymm', 'postal_code', 'median_listing_price',  'active_listing_count', 'median_days_on_market', 'new_listing_count', 'price_increased_count', 'price_reduced_count']
cols_hot = ['month_date_yyyymm', 'postal_code', 'hotness_rank', 'hotness_rank_mm', 'hotness_rank_yy', 'hotness_score', 'supply_score', 'demand_score']

@st.cache_data
def load_data():
    # Added logging for debugging purposes
    st.write("Loading data from URLs...")
    
    # Read in the datasets
    inv = pd.read_csv(url, low_memory=False, usecols=cols, sep=',')[:-1] # Drop contact info row
    inv['month_date_yyyymm'] = pd.to_datetime(inv['month_date_yyyymm'], format='%Y%m')
    
    h = pd.read_csv(url_hot, low_memory=False, usecols=cols_hot, sep=',')[:-1] # Drop contact info row
    h['month_date_yyyymm'] = pd.to_datetime(h['month_date_yyyymm'], format='%Y%m')
    
    # Merge datasets
    d = pd.merge(inv, h, how="inner", on=['month_date_yyyymm', 'postal_code'])
    
    # Memory optimization
    def reduce_mem_usage(df):
        for col in df.columns:
            col_type = df[col].dtype
            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.uint8).min and c_max < np.iinfo(np.uint8).max:
                        df[col] = df[col].astype(np.uint8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.uint16).min and c_max < np.iinfo(np.uint16).max:
                        df[col] = df[col].astype(np.uint16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.uint32).min and c_max < np.iinfo(np.uint32).max:
                        df[col] = df[col].astype(np.uint32)                    
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)
                    elif c_min > np.iinfo(np.uint64).min and c_max < np.iinfo(np.uint64).max:
                        df[col] = df[col].astype(np.uint64)
                elif str(col_type)[:5] == 'float':
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
    reduce_mem_usage(d)
    
    # Added logging for confirmation of data loading
    st.write("Data successfully loaded and memory optimized.")
    
    return d

# Load data into a dataframe
df = load_data()

# Create 2 columns layout
col1, col2 = st.columns([20, 5])

# Title column
with col1:
    st.title("Housing Market Trends by Zip Code")

# Zip selector column
with col2:
    zip_input = st.selectbox("What zip code?", sorted(list(df.postal_code.unique())))

# Display description
st.markdown("This dashboard pulls in summary market metrics for all zip codes in the US and shows their trends over time. Use it to track median prices, price changes, new listings, and active inventory in your zip code of interest.")
st.write("Source: Realtor.com [Research Data](https://www.realtor.com/research/data/)")

# Static table of sample locations
data = {
    'Location': ['Broken Bow, OK', 'Blue Ridge, GA', 'Sevierville, TN', 'Gatlinburg, TN', 'Pigeon Forge, TN', 'Madison, MS', 'Canton, MS', 'North Myrtle', 'Surfside Beach' ],
    'Zip Code(s)': ['74728', '30513, 30522, 30560', '37862, 37876, 37864', '37738', '37863, 37868', '39110', '39046', '29582', '29575']
}
codes = pd.DataFrame(data)
st.table(codes)

# Filter the dataframe by the selected zip code
df_tgt = df[df['postal_code'] == zip_input].sort_values('month_date_yyyymm', ascending=True)

# Plot each chart
def plot_chart(data, x, y, title):
    fig = px.line(data, x=x, y=y, title=title, markers=True)
    st.plotly_chart(fig, use_container_width=True)

# Create charts
plot_chart(df_tgt, 'month_date_yyyymm', 'median_listing_price', 'Median Listing Price in ' + zip_input)
plot_chart(df_tgt, 'month_date_yyyymm', 'active_listing_count', 'Monthly Active Listing Count in ' + zip_input)
plot_chart(df_tgt, 'month_date_yyyymm', 'median_days_on_market', 'Median Days On Market in ' + zip_input)
plot_chart(df_tgt, 'month_date_yyyymm', 'new_listing_count', 'Monthly New Listing Count in ' + zip_input)
plot_chart(df_tgt, 'month_date_yyyymm', 'price_increased_count', 'Monthly Price Increase Count in ' + zip_input)
plot_chart(df_tgt, 'month_date_yyyymm', 'price_reduced_count', 'Monthly Price Reduced Count in ' + zip_input)
plot_chart(df_tgt, 'month_date_yyyymm', 'hotness_rank', 'Hotness Rank in ' + zip_input)
