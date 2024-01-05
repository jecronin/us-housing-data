#import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import geocoder
from datetime import datetime
st.set_page_config(layout="wide")
# -- Read in the data
url = "https://cdn-charts.streeteasy.com/rentals/OneBd/medianAskingRent_OneBd.zip"
url2 = "https://cdn-charts.streeteasy.com/rentals/TwoBd/medianAskingRent_TwoBd.zip"
url3 = "https://cdn-charts.streeteasy.com/rentals/ThreePlusBd/medianAskingRent_ThreePlusBd.zip"
@st.cache_data
def load_data():
    df = pd.read_csv(url)
    df2 = pd.read_csv(url2)
    df3 = pd.read_csv(url3)
    df['bed'] = 1
    df2['bed'] = 2
    df3['bed'] = 3
    series_list = df.drop(columns=['areaName', 'Borough', 'areaType', 'bed']).columns.to_list()
    melt1 = pd.melt(df, id_vars=['areaName', 'Borough', 'areaType','bed'], value_vars=series_list, value_name='Rent').sort_values(['areaName','variable'])
    melt2 = pd.melt(df2, id_vars=['areaName', 'Borough', 'areaType','bed'], value_vars=series_list, value_name='Rent').sort_values(['areaName','variable'])
    melt3 = pd.melt(df3, id_vars=['areaName', 'Borough', 'areaType','bed'], value_vars=series_list, value_name='Rent').sort_values(['areaName','variable'])
    d = pd.concat([melt1,melt2,melt3])
    d.columns = ['areaName', 'Borough', 'areaType', 'bed', 'Month', 'Rent']
    d['Month'] = pd.to_datetime(d.Month)
    d['Year'] = d['Month'].dt.strftime('%Y')
    d['Year'] = d['Year'].str.replace(',', '').astype(int)
    hood_df = pd.read_csv('https://raw.githubusercontent.com/jecronin/us-housing-data/main/nyc_neighborhood_coordinates.csv', usecols=['neighborhood','latitude','longitude'], sep=',',low_memory=False)
    d = pd.merge(d, hood_df, left_on="areaName", right_on="neighborhood", how="inner" )
    d = d.drop(columns="neighborhood")
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
    columns_to_round = [col for col in d.columns if col not in ['lat', 'lng']]
    d[columns_to_round] = d[columns_to_round].round(2)
    return d
df_melt = load_data()
#Create 2 columns
st.title("NYC Rent Data Dashboard")
st.dataframe(df_melt)
df_year = df_melt.groupby(['areaName', 'Borough', 'areaType','bed', 'Year']).agg({'Rent':'mean'}).reset_index()
st.dataframe(df_year)
selected_area_name = st.selectbox("Select Area Name", df_year['areaName'].unique())

filtered_df = df_year[(df_year['areaName'] == selected_area_name)]

fig = px.line(labels={'Year': 'Year', 'Rent': 'Rent'}, title=f'Rent Trend Over Time for Bedrooms in {selected_area_name}')

for b in [1, 2, 3]:
    df_filtered_bed = filtered_df[filtered_df.bed == b]
    fig.add_scatter(x=df_filtered_bed['Year'], y=df_filtered_bed['Rent'], name=f"{b} Bedroom")

st.plotly_chart(fig)
