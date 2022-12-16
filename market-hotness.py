#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import geocoder
from datetime import datetime
st.set_page_config(layout="wide")
# -- Read in the data
url = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Hotness/RDC_Inventory_Hotness_Metrics_Zip_History.csv"
cols = ['month_date_yyyymm', 'postal_code', 'zip_name', 'hotness_rank', 'hotness_rank_mm', 'hotness_rank_yy', 'hotness_score',
       'supply_score', 'demand_score']
@st.cache
def load_data():
    d = pd.read_csv(url, low_memory=False, usecols=cols, sep=',')[:-1] #read in csv and drop the last row of contact information
    d = d.drop_duplicates()
    d['month_date_yyyymm'] = pd.to_datetime(d['month_date_yyyymm'], format='%Y%m') #convert date to datetime
    d['zip_name'] = d['zip_name'].fillna('N/A')
    d['state'] = d['zip_name'].str[-2:]
    for col in ['hotness_rank_mm', 'hotness_rank_yy']:
       d[col] = d[col].fillna(0)    
#reduce memory of dataframe
    def reduce_mem_usage(d):
        for col in d.columns:
            col_type = d[col].dtype
        if col_type != object:
                c_min = d[col].min()
                c_max = d[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        d[col] = d[col].astype(np.int8)
                    elif c_min > np.iinfo(np.uint8).min and c_max < np.iinfo(np.uint8).max:
                        d[col] = d[col].astype(np.uint8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        d[col] = d[col].astype(np.int16)
                    elif c_min > np.iinfo(np.uint16).min and c_max < np.iinfo(np.uint16).max:
                        d[col] = d[col].astype(np.uint16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        d[col] = d[col].astype(np.int32)
                    elif c_min > np.iinfo(np.uint32).min and c_max < np.iinfo(np.uint32).max:
                        d[col] = d[col].astype(np.uint32)                    
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        d[col] = d[col].astype(np.int64)
                    elif c_min > np.iinfo(np.uint64).min and c_max < np.iinfo(np.uint64).max:
                        d[col] = d[col].astype(np.uint64)
                elif str(col_type)[:5] == 'float':
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        d[col] = d[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        d[col] = d[col].astype(np.float32)
                    else:
                        d[col] = d[col].astype(np.float64)
    reduce_mem_usage(d)
    return d
df = load_data()
#Create 2 columns
st.title("Market hotness data dashboard")

col1,col2,col3 = st.columns([5,5,5])

with col1:
       zip_input = st.selectbox("What zip code?", sorted(list(df.postal_code.unique())))
with col2:
       supply_slider = st.slider("Supply score: ", value=0, min_value=0,max_value=100)
with col3:
       demand_slider = st.slider("Demand score: ", value=0, min_value=0,max_value=100)
       
# -- We use the first column here as a dummy to add a space to the left
st.markdown("This dashboard pulls in market hotness metrics across the US")
st.write("Source: Realtor.com [Research Data](https://www.realtor.com/research/data/)")

df_tgt = df[df['postal_code'] == zip_input].sort_values('month_date_yyyymm', ascending=True)
st.dataframe(df[(df['supply_score'] >= supply_slider)&(df['demand_score'] >= demand_slider)].sort_values('month_date_yyyymm', ascending=False))
fig = px.line(df_tgt,
                x='month_date_yyyymm',
                y='hotness_score',
                title = "Hotness score in " + zip_input,
                markers=True
)

# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)
