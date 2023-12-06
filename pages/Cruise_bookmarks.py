import random
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.switch_page_button import switch_page 

from backend.Sharks_utils_v1 import define_clusters, clean_clusters_centerpoints, compute_maritime_route
from backend.Sharks_streamlit_utils_v1 import get_session_state, order_and_hide_pages, initialize_state_saves
from pages.CRUISE_new import render_mapbox_cruise

df_countries =pd.read_csv('input_data/plotly_countries_and_codes.xls').filter(['COUNTRY','CODE']).assign(selected = False)
var_list = get_session_state(['transformed_data/sharks', 'transformed_data/activities_words'])
sharks, activities = var_list[0], var_list[1]

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "centered", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()

#Select book mark

selected_bookmark = st.selectbox('Bookmarks',options=[x for x in st.session_state['_cruise_bookmarks_'].keys() if x != 'temp_save'],index = None, placeholder='Select a bookmarked cruise')

if selected_bookmark == None:
    st.info('Select a bookmarked cruise to be displayed')
else:
    dfPorts = pd.read_csv('input_data/ports.csv').filter(['Main Port Name','Country Code','Latitude','Longitude']).rename(columns = {'Main Port Name':'Port','Country Code':'Country'})
    var_list = get_session_state(['transformed_data/sharks'])
    sharks = var_list[0]
    sharks['coordinates'] = sharks.filter(['latitude', 'longitude']).values.tolist()


    #Retrieve cruise
    #-------------------------------------------------------------
    departure_country = st.session_state['_cruise_bookmarks_'][selected_bookmark]['departure_country']
    period_start = st.session_state['_cruise_bookmarks_'][selected_bookmark]['period_start']
    period_end = st.session_state['_cruise_bookmarks_'][selected_bookmark]['period_end']
    cruise_stages = st.session_state['_cruise_bookmarks_'][selected_bookmark]['cruise_stages']
    waypoints = st.session_state['_cruise_bookmarks_'][selected_bookmark]['waypoints']
    dfActivities_locations = st.session_state['_cruise_bookmarks_'][selected_bookmark]['dfActivities_locations']


    # Display cruise
    #-------------------------------------------------------------
    departure_port = dfPorts.query('Country == @departure_country').sample(1)
    departure_lat = departure_port.Latitude.values[0]
    departure_lon = departure_port.Longitude.values[0]

    c1,c2,c3,c4 = st.columns([2,2,2,1])
    c1.info(f'Parameters : \n- **{cruise_stages}** activities among :  {",".join(st.session_state["_type_activities_"])} \n - Cruise path based on data from *{period_start}* to *{period_end}* ')
    c2.success(f'Departure Harbor :\n- **{departure_port.Port.values[0]}** ({departure_country})')

    #Filter out data not in study period & extract coordinates for clustering analysis
    #-------------------------------------------------------------
    sharks_selection = sharks.query("year >= @period_start").query("year <= @period_end").copy()
    selected_attacks_coordinates = sharks_selection.filter(['latitude', 'longitude']).dropna().values

    diffs=np.diff(lons:=waypoints.lon.values) #Compute diff in long with next position
    #the number 180 depends on your "step size", may need customization
    crossings_plusminus=np.where(diffs<=-180)[0]
    crossing_minusplus=np.where(diffs>180)[0]
    for plusmin_crossing in crossings_plusminus:
        lons[plusmin_crossing+1:]+=360
    for minusplus_crossing in crossing_minusplus:
        lons[minusplus_crossing+1:]-=360

        
    #Build the Map
    #-------------------------------------------------------------
    fig = render_mapbox_cruise(sharks_selection)
    fig.update_layout(height=700)

    #Cruise
    #-------------------------------------------------------------
    fig.add_trace(go.Scattermapbox(lat = waypoints.lat,
                                        lon = lons,
                                        mode = 'lines',
                                        line = dict(color = 'grey'),
                                        name = 'CRUISE'))

    #Activities
    #-------------------------------------------------------------
    activities_color_map = {'Departure':'yellow',
                            'surfing':'rgb(141,211,199)','swimming':'rgb(255,255,179)','fishing':'rgb(190,186,218)','diving':'rgb(251,128,114)',
                            'spearfishing':'rgb(128,177,211)','bathing':'rgb(253,180,98)','wading':'rgb(179,222,105)','scuba':'rgb(252,205,229)',
                            'snorkeling':'rgb(217,217,217)','kayaking':'rgb(188,128,189)',}

    for activity in dfActivities_locations.activity.unique().tolist():
        #Border
        fig.add_trace(go.Scattermapbox(lat = dfActivities_locations.query('activity == @activity').lat,
                                            lon = dfActivities_locations.query('activity == @activity').lon,
                                            mode = 'markers',
                                            marker = dict(color = 'black',size = 26,),
                                            name = activity,
                                            showlegend = False))
        #Activity
        fig.add_trace(go.Scattermapbox(lat = dfActivities_locations.query('activity == @activity').lat,
                                            lon = dfActivities_locations.query('activity == @activity').lon,
                                            mode = 'markers',
                                            marker = dict(color = activities_color_map[dfActivities_locations.query('activity == @activity').activity.unique().tolist()[0]],size = 20,),
                                            name = activity))

    #Render the map & generate
    st.plotly_chart(fig, use_container_width= True)