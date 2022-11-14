import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(layout="wide")
# -- Read in the data
url = "https://econdata.s3-us-west-2.amazonaws.com/Reports/Core/RDC_Inventory_Core_Metrics_Zip_History.csv"
cols = ['month_date_yyyymm', 'postal_code', 'zip_name','median_listing_price',  'active_listing_count','median_days_on_market']
#data_dic = {'month_date_yyyymm':'string', 'postal_code':'string', 'zip_name':'string','median_listing_price':'int64',  'active_listing_count':'int32','median_days_on_market':'int32'}
df = pd.read_csv(url, usecols=cols)
df.drop(df.tail(1).index,inplace=True) # drop last row that has data RDC contact info
for col in list(df.select_dtypes(['object']).columns):
  df[col] = df[col].astype('string')
  
zip_list = ("74728", "94123", "11211", "11249", "30560", "39110", "95670")
#Create 3 columns
col1, col2, col3 = st.columns([5, 5, 20])
# -- Put the image in the middle column
# - Commented out here so that the file will run without having the image downloaded
with col2:
  zip_input = st.selectbox("What zip code?", zip_list)
# -- Put the title in the last column
with col3:
    st.title("Housing Market Trends by Zip Code")
# -- We use the first column here as a dummy to add a space to the left

df_tgt = df[df['postal_code'] == zip_input].sort_values('month_date_yyyymm', ascending=True)
fig = px.line(df_tgt,
                x='month_date_yyyymm',
                y='median_listing_price',
                title = 'list_price' + " in " + zip_input,
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
