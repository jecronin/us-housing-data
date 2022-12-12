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
cols = ['month_date_yyyymm', 'postal_code', 'zip_name', 'median_listing_price',  'active_listing_count','median_days_on_market', 'new_listing_count', 'price_increased_count', 'price_reduced_count'] #add back zip name when want to use
cols_hot = ['month_date_yyyymm', 'postal_code', 'hotness_rank', 'hotness_rank_mm', 'hotness_rank_yy', 'hotness_score',
       'supply_score', 'demand_score']
#data_dic = {'month_date_yyyymm':'string', 'postal_code':'string', 'zip_name':'string','median_listing_price':'int64',  'active_listing_count':'int32','median_days_on_market':'int32'}
@st.cache
def load_data():
    inv = pd.read_csv(url, low_memory=False, usecols=cols, sep=',')[:-1] #read in csv and drop the last row of contact information
    inv['month_date_yyyymm'] = pd.to_datetime(inv['month_date_yyyymm'], format='%Y%m') #convert date to datetime
    h = pd.read_csv(url_hot, low_memory=False, usecols=cols_hot, sep=',')[:-1] #read in csv and drop the last row of contact information
    h['month_date_yyyymm'] = pd.to_datetime(h['month_date_yyyymm'], format='%Y%m') #convert date to datetime
    d = pd.merge(inv,h, how="inner", on=['month_date_yyyymm', 'postal_code'])
    d['zip_code_name'] = d.postal_code.apply(str) + ' / ' + d.zip_name
    d['zip_code_name'] = d.zip_code_name.astype('string')
    d.drop('zip_name', axis=1, inplace=True)
    d.drop('postal_code', axis=1, inplace=True)
    del inv
    del h
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
col1, col2 = st.columns([20,5])
#Title column
with col1:
    st.title("Housing Market Trends by Zip Code")
#Zip selector column
with col2:
  zip_input = st.selectbox("What zip code?", sorted(list(df.zip_code_name.unique())))
# -- We use the first column here as a dummy to add a space to the left
st.markdown("This dashboard pulls in summary market metrics for all zip codes in the US and shows their trends over time. Use it to track median prices, price changes,  new listings and active inventory in your zip code of interest.")
st.write("Source: Realtor.com [Research Data](https://www.realtor.com/research/data/)")

df_tgt = df[df['zip_code_name'] == zip_input].sort_values('month_date_yyyymm', ascending=True)
fig = px.line(df_tgt,
                x='month_date_yyyymm',
                y='median_listing_price',
                title = 'Median Listing Price' + " in " + zip_input,
                markers=True
)

# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)

fig2 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='active_listing_count',
                title = 'Monthly Active Listing Count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='median_days_on_market',
                title = 'Median Days On Market' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='new_listing_count',
                title = 'Monthly New Listing Count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig4, use_container_width=True)

fig5 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='price_increased_count',
                title = 'Monthly Price Increase Count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig5, use_container_width=True)

fig6 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='price_reduced_count',
                title = 'Monthly Price Reduced Count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig6, use_container_width=True)

fig7 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='hotness_rank',
                title = 'Hotness Rank' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig7, use_container_width=True)
