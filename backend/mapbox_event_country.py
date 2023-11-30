#pip install streamlit-plotly-mapboxEvents
import streamlit as st
from streamlit_plotly_mapbox_events import plotly_mapbox_events
import geopandas as gpd
import plotly.express as px
import json

with open('countries.geojson') as response:
    polygons = json.load(response)
dj = gpd.GeoDataFrame.from_features(polygons) #.drop_duplicates(subset='ISO_A3')
dj.loc[dj.ISO_A3 == '-99','ISO_A3'] = dj.loc[dj.ISO_A3 == '-99','ADMIN'].str[:2]
dj = dj.set_index('ISO_A3')

dj


mapbox_fig = px.choropleth_mapbox(dj,
                                    geojson=dj.geometry,
                                    locations= dj.index,
                                    #color=dj.ADMIN,
                                    mapbox_style="carto-positron",
                                    #color_continuous_scale="Reds",
                                    opacity=0.5,
                                    zoom=1,
                                    height= 800
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