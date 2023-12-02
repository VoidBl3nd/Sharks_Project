import pandas as pd
import streamlit as st
from typing import Set
from typing import Dict
import plotly.express as px
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

df =pd.read_csv('input_data/plotly_countries_and_codes.xls').filter(['COUNTRY','CODE'])
df['selected'] = False

def initialize_state():
    """Initializes all Session State variables"""

    for session_name in ['_selected_country_','_due_to_rerun_', '_selected_index_', '_curve_number_', '_widget_rerun_']:
        if session_name not in st.session_state:
            st.session_state[session_name] = 0

def build_plotly_chart(df):
    """Build a plotly chloropleth map used to select countries"""
    #Build figure
    #---------------------------------------------------
    fig = px.choropleth(df,
                        locations="CODE",
                        color = 'selected',
                        hover_name="COUNTRY",
                        template = 'seaborn',
                        color_discrete_sequence= ['#76b0a6', 'rgb(255,255,179)'],
                        projection="orthographic",
                        hover_data= {'selected': False, 'CODE':False}
    )
    fig.update_geos(showcoastlines=True, coastlinecolor = '#afe3e0',
                    showland=True, landcolor='White',
                    showocean=True, oceancolor= '#50545c',
                    showlakes=False, )#Otherwise lake are showing white
    fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)')) #Color when zoom out of map
    fig.add_trace(go.Choropleth(locations=['ATA'],z=[0],colorscale=[[0,'#76b0a6'], [1,'#76b0a6']],showlegend=False,showscale=False)) #color Antartica

    #Make it kind to the eye in Streamlit
    #---------------------------------------------------
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0),paper_bgcolor="rgba(0, 0, 0, 0)") # Remove margin and make remaining background transparent
    fig.update_layout(showlegend=False) # Remove legend

    return fig

def render_plotly_chart(df):
    #Select a country (only if no country yet selected)
    #---------------------------------------------------
    if '_selected_country_' not in st.session_state or st.session_state['_selected_country_'] == 0:
        fig = build_plotly_chart(df)
        map_selection = plotly_events(fig, select_event=True, key=f"_country_selector_")
        if map_selection != []:
            selected_index = map_selection[0]['pointNumber']
            st.session_state['_selected_country_'] = df.iloc[selected_index].COUNTRY
            need_update = True
        else:
            need_update = False

    #Display selection
    #---------------------------------------------------
    else:
        selected_country = st.session_state['_selected_country_']
        df.loc[df.COUNTRY == selected_country, 'selected'] = True
        fig = build_plotly_chart(df)
        st.plotly_chart(fig)
        need_update = False

    return need_update
        
if __name__ == "__main__":
    print('Please launch in Streamlit')