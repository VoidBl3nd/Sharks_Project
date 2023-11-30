#pip install streamlit-plotly-mapboxEvents
import streamlit as st
from streamlit_plotly_mapbox_events import plotly_mapbox_events
import geopandas as gpd
import plotly.express as px
import json

import requests
import numpy as np

cont = requests.get(
    "https://gist.githubusercontent.com/hrbrmstr/91ea5cc9474286c72838/raw/59421ff9b268ff0929b051ddafafbeb94a4c1910/continents.json"
)

gdf = gpd.GeoDataFrame.from_features(cont.json())



mapbox_fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry,
    locations=gdf.index,
    #color=gdf.index,
    mapbox_style="carto-positron",
    #color_continuous_scale="Reds",
    opacity=0.5,
    zoom=0,
)


mapbox_events = plotly_mapbox_events(
    mapbox_fig,
    click_event=True,
    select_event=True,)
    #hover_event=True,
    #relayout_event=True)


plot_name_holder_clicked = st.empty()
plot_name_holder_selected = st.empty()
plot_name_holder_hovered = st.empty()
plot_name_holder_relayout = st.empty()

plot_name_holder_clicked.write(f"Clicked Point: {mapbox_events[0]}")
plot_name_holder_selected.write(f"Selected Point: {mapbox_events[1]}")
#plot_name_holder_hovered.write(f"Hovered Point: {mapbox_events[2]}")
#plot_name_holder_relayout.write(f"Relayout: {mapbox_events[3]}")
print('hi')