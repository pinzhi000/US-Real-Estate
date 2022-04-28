# import libraries 

import streamlit as st 
from streamlit_folium import folium_static

import pandas as pd
import geopandas as gpd

import folium 
from folium.features import GeoJsonPopup, GeoJsonTooltip


# step 1: import & filter data 

# cache decorator 
    # allows your app to stay performant when loading, reading or manipulating large amount of data that may cause expensive computations 
@st.cache
def read_csv(path):
    return pd.read_csv(path, compression='gzip', sep='\t', quotechar='"')

# data prep to get relevant fields from input dataset
housing_price_df = read_csv('C:/Users/Pinzhi Zhang/Desktop/Georgia_Tech/7_Spring_2022/CSE 6242/Streamlit/US Real Estate/state_market_tracker.tsv000.gz')
housing_price_df = housing_price_df[['period_begin','period_end','period_duration','property_type','median_sale_price','median_sale_price_yoy','homes_sold','state_code']]
housing_price_df = housing_price_df[(housing_price_df['period_begin'] >= '2020-10-01') & (housing_price_df['period_begin'] <= '2021-10-01')]

# st.write(housing_price_df)  


# read in geojson file 
@st.cache
def read_file(path):
    return gpd.read_file(path)

# read geojson file 
gdf = read_file('C:/Users/Pinzhi Zhang/Desktop/Georgia_Tech/7_Spring_2022/CSE 6242/Streamlit/US Real Estate/us-state-boundaries.geojson') 
# st.write(gdf.head())


# merge housing market data and geojson file into one dataframe 
df_final = gdf.merge(housing_price_df, left_on="stusab", right_on="state_code", how="outer")
df_final = df_final[['period_begin','period_end','period_duration','property_type','median_sale_price','median_sale_price_yoy','homes_sold','state_code','name','stusab','geometry']]
df_final = df_final[~df_final['period_begin'].isna()]
# st.write(df_final.head(20))


# step 2: display intro info 

# add sidebar 
st.sidebar.markdown("### My First Streamlit Site")
st.sidebar.markdown("Welcome to my first attempt at building an interactive viz in Streamlit. This app uses a data source from redfin housing market site. And so it begins!")

# add title and subtitle to main interface of the app
st.title("US Real Estate Insights")
st.markdown("Where are the hottest housing markets in the US?  Select the housing market metrics you are interested in and your insights are just a couple clicks away. Hover over the map to view more details.")

# add webpage filters 
    # create 3 column filters 
col1, col2, col3 = st.columns(3)

with col1:
    period_list = df_final["period_begin"].unique().tolist()
    period_list.sort(reverse=True)
    year_month = st.selectbox("Snapshot Month", period_list, index=0)

with col2:
    prop_type = st.selectbox("View by Property Type", ['All Residential', 'Single Family Residential', 'Townhouse','Condo/Co-op','Single Units Only','Multi-Family (2-4 Unit)'], index=0)

with col3:
    # select a specific column from dataset  
    metrics = st.selectbox("Select Housing Metrics", ["median_sale_price", "median_sale_price_yoy", "homes_sold"], index=0)


# update data frame accordingly based on user input 
df_final = df_final[df_final["period_begin"]==year_month]
df_final = df_final[df_final["property_type"]==prop_type]
df_final=df_final[['period_begin','period_end','period_duration','property_type',metrics,'state_code','name','stusab','geometry']]

# st.write(df_final)



# step 2: create map 

# initiate a folium map 
m = folium.Map(location = [40, -100], zoom_start = 4, tiles = None)
folium.TileLayer('CartoDB positron', name = "Light Map", control=False).add_to(m)

# plot choropleth map using folium 
choropleth1 = folium.Choropleth(
    geo_data = 'C:/Users/Pinzhi Zhang/Desktop/Georgia_Tech/7_Spring_2022/CSE 6242/Streamlit/US Real Estate/us-state-boundaries.geojson',
    name = "Choropleth Map of U.S. Housing Prices", 
    data = df_final,
    # 2 columns in dataframe used to grab the median sales price for each state and plot it in the choropleth map
    columns = ['state_code', metrics],
    # key in geojson file used to grab the geometries for each state in order to add the geographical boundary layers to the map
    key_on = 'feature.properties.stusab',
    # fill color changes based on value of housing metric selected
    fill_color = "YlOrRd",
    nan_fill_color = "White", 
    fill_opacity = 0.7,
    line_opacity = 0.2,
    legend_name = 'Housing Market Metrics', 
    highlight = True,
    line_color = 'black').geojson.add_to(m)




# step 3: add tooltips to map; info appears on hover 
geojson1 = folium.features.GeoJson(
    data = df_final, 
    name = "USA Housing Prices",
    smooth_factor = 2,
    style_function = lambda x: {'color':'gray', 'fillColor':'transparent', 'weight':0.1},
    # set tooltip
    tooltip = folium.features.GeoJsonTooltip(
        fields = ['period_begin',
                  'period_end',
                  'name',
                  metrics,],
        aliases = ['Period Begin:', 
                    'Period End:', 
                    'State', 
                    metrics+":"],
        localize = True,
        sticky = False,
        labels = True,
        style = """
            background-color: #F0EFEF;
            border: 2px solid grey;
            border-radius: 2px; 
            box-shadow: 3px;
        """,
        max_width = 600,),
        highlight_function = lambda x: {'weight':3, 'fillColor':'grey'},
    ).add_to(m)

# apply characteristics to map 
folium_static(m)