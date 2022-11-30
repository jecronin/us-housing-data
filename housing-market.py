import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
st.set_page_config(layout="wide")
# -- Read in the data
url = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"
cols = ['month_date_yyyymm', 'postal_code','median_listing_price',  'active_listing_count','median_days_on_market', 'new_listing_count', 'price_increased_count', 'price_reduced_count'] #add back zip name when want to use
#data_dic = {'month_date_yyyymm':'string', 'postal_code':'string', 'zip_name':'string','median_listing_price':'int64',  'active_listing_count':'int32','median_days_on_market':'int32'}
df = pd.read_csv(url, low_memory=False, usecols=cols, sep=',') #read in csv
df.drop(df.tail(1).index,inplace=True) # drop last row that has data RDC contact info                                 
tgt_zips = sorted(['74728', '94123', '11211', '11249', '30560', '39110', '95670', '35004', '35007', '35094'])#set target list of zips
df = df[df.postal_code.isin(tgt_zips)] #filter df
df['month_date_yyyymm'] = pd.to_datetime(df['month_date_yyyymm'], format='%Y%m') #convert date to datetime
#reduce memory of dataframe
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
reduce_mem_usage(df)

#Create 3 columns
col1, col2, col3 = st.columns([5, 5, 20])
# -- Put the image in the middle column
# - Commented out here so that the file will run without having the image downloaded
with col1:
    st.markdown('Source: Realtor.com Research Data')
with col2:
  zip_input = st.selectbox("What zip code?", tgt_zips)
# -- Put the title in the last column
with col3:
    st.title("Housing Market Trends by Zip Code")
# -- We use the first column here as a dummy to add a space to the left

df_tgt = df[df['postal_code'] == zip_input].sort_values('month_date_yyyymm', ascending=True)
fig = px.line(df_tgt,
                x='month_date_yyyymm',
                y='median_listing_price',
                title = 'Median Listing Price' + " in " + zip_input + "-" + df[df['postal_code'] == zip_input]['zip_name'].iloc[0],
                markers=True
)

# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig, use_container_width=True)

fig2 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='active_listing_count',
                title = 'active_listing_count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='median_days_on_market',
                title = 'median_days' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='new_listing_count',
                title = 'new_listing_count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig4, use_container_width=True)

fig5 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='price_increased_count',
                title = 'price_increased_count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig5, use_container_width=True)

fig6 = px.line(df_tgt,
                x='month_date_yyyymm',
                y='price_reduced_count',
                title = 'price_reduced_count' + " in " + zip_input,
                markers=True
)
# -- Input the Plotly chart to the Streamlit interface
st.plotly_chart(fig6, use_container_width=True)
