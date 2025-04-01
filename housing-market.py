# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import logging

st.set_page_config(layout="wide")

# -- URLs for datasets
URL_INV = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"
URL_HOT = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Hotness/RDC_Inventory_Hotness_Metrics_Zip_History.csv"

COLUMNS_INV = [
    'month_date_yyyymm', 'postal_code', 'median_listing_price',
    'active_listing_count', 'median_days_on_market', 'new_listing_count',
    'price_increased_count', 'price_reduced_count'
]

COLUMNS_HOT = [
    'month_date_yyyymm', 'postal_code', 'hotness_rank', 'hotness_rank_mm',
    'hotness_rank_yy', 'hotness_score', 'supply_score', 'demand_score'
]

@st.cache_data
def load_data():
    inv = pd.read_csv(URL_INV, usecols=COLUMNS_INV, dtype_backend="pyarrow")
    inv = inv[inv['postal_code'].notna()]
    inv['month_date_yyyymm'] = pd.to_datetime(inv['month_date_yyyymm'], format='%Y%m')
    inv['postal_code'] = inv['postal_code'].astype(str)

    hot = pd.read_csv(URL_HOT, usecols=COLUMNS_HOT, dtype_backend="pyarrow")
    hot = hot[hot['postal_code'].notna()]
    hot['month_date_yyyymm'] = pd.to_datetime(hot['month_date_yyyymm'], format='%Y%m')
    hot['postal_code'] = hot['postal_code'].astype(str)

    df = pd.merge(inv, hot, how="inner", on=['month_date_yyyymm', 'postal_code'])
    df['postal_code'] = df['postal_code'].astype(str)
    return df

with st.spinner("Loading data..."):
    df = load_data()

zip_list = sorted(df['postal_code'].dropna().astype(str).unique())

# Create layout columns
col1, col2 = st.columns([20, 5])

# Title
with col1:
    st.title("Housing Market Trends by Zip Code")

# Zip selector
with col2:
    zip_input = st.selectbox("What zip code?", zip_list)

st.markdown("""
This dashboard pulls in summary market metrics for all zip codes in the US and shows their trends over time. 
Use it to track median prices, price changes, new listings, and active inventory in your zip code of interest.
""")
st.write("Source: Realtor.com [Research Data](https://www.realtor.com/research/data/)")

# Sample ZIP table
data = {
    'Location': ['Broken Bow, OK', 'Blue Ridge, GA', 'Sevierville, TN', 'Gatlinburg, TN',
                 'Pigeon Forge, TN', 'Madison, MS', 'Canton, MS', 'North Myrtle', 'Surfside Beach', 'Columbus, OH'],
    'Zip Code(s)': ['74728', '30513, 30522, 30560', '37862, 37876, 37864', '37738',
                    '37863, 37868', '39110', '39046', '29582', '29575', '43206']
}
st.table(pd.DataFrame(data))

# Filter data for selected ZIP
df_tgt = df[df['postal_code'] == zip_input].sort_values('month_date_yyyymm').reset_index(drop=True)
df_tgt['yoy_list_price'] = df_tgt['median_listing_price'].pct_change(periods=12) * 100 # Assuming monthly data

# Preview of data
st.subheader("Preview of Realtor.com Housing Data")
st.dataframe(df_tgt)

for col in ['median_listing_price',
    'active_listing_count', 'median_days_on_market', 'new_listing_count',
    'price_increased_count', 'price_reduced_count', 'hotness_rank']:
        st.line_chart(df_tgt, x="month_date_yyyymm", y=col)
                      
