import random
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.switch_page_button import switch_page 

from backend.cruise_utils import define_clusters, clean_clusters_centerpoints, compute_maritime_route
from backend.Sharks_streamlit_utils_v1 import get_session_state, order_and_hide_pages, initialize_state_saves, render_mapbox_cruise, activities_mapping

cluster_distance = 10 #10 #km : maximum_distance_within_cluster
cluster_minsize = 5 #5 #minimum_number_attacks_within_cluster
#min_cruise_stages = 1
#max_cruise_stages = 5
dfPorts = pd.read_csv('input_data/ports.csv').filter(['Main Port Name','Country Code','Latitude','Longitude']).rename(columns = {'Main Port Name':'Port','Country Code':'Country'})

var_list = get_session_state(['transformed_data/sharks'])
sharks = var_list[0]
sharks['coordinates'] = sharks.filter(['latitude', 'longitude']).values.tolist()

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space
order_and_hide_pages()
initialize_state_saves()

if '_selected_country_' not in st.session_state:
    st.info('Please select a departure country in the Home page')
else:
    if st.session_state['_selected_country_'] == 0:
        st.info('Please select a departure country in the Home page')
    else:
        departure_country = st.session_state['_selected_country_']
        period_start = st.session_state['_start_year_']
        period_end = st.session_state['_end_year_']
        cruise_stages = st.session_state['_number_activities_']
        if dfPorts.query('Country == @departure_country').empty:
            st.warning("Please select another country. This one doesn't have any harbor we can start the cruise with.")
        else:

            #Select random Harbor among available within departure country
            #-------------------------------------------------------------
            departure_port = dfPorts.query('Country == @departure_country').sample(1)
            departure_lat = departure_port.Latitude.values[0]
            departure_lon = departure_port.Longitude.values[0]

            c1,c2,c3,c4,c5,c6 = st.columns([5,5,5,1,2,1])
            c1.info(f'Parameters : \n- **{cruise_stages}** activities among :  {",".join(st.session_state["_type_activities_"])} \n - Cruise path based on data from *{period_start}* to *{period_end}* ')
            c2.success(f'Departure Harbor :\n- **{departure_port.Port.values[0]}** ({departure_country})')
            if c3.button('Change parameters',type = 'secondary', use_container_width= True):
                switch_page('Generate')

            #c3.write('t')
            c3.button('🔄 Generate an alternative cruise', type = 'primary',use_container_width= True)


            #Filter out data not in study period & extract coordinates for clustering analysis
            #-------------------------------------------------------------
            sharks_selection = sharks.query("year >= @period_start").query("year <= @period_end").copy()
            selected_attacks_coordinates = sharks_selection.filter(['latitude', 'longitude']).dropna().values
            #sharks_selection = sharks.copy()
            #sharks_selection['selection'] = 'excluded'
            #sharks_selection.loc[(sharks_selection.year >= period_start) & (sharks_selection.year <= period_start),'selection'] = 'selected'

            #Generate clusters & their center point
            #-------------------------------------------------------------
            dfcluster, clusters, results_print = define_clusters(selected_attacks_coordinates, max_km_btwn_points_in_cluster=cluster_distance, min_cluster_size=cluster_minsize)

            #with st.sidebar:
            #    st.markdown('Dropped entries without coordinates: {}'.format(sharks_selection.filter(['latitude', 'longitude']).isna().any(axis=1).sum()))
            #    for i in results_print:
            #        st.markdown(i)

            dfCenters = clean_clusters_centerpoints(clusters)
            dfCenters['cluster'] = "Cluster n°" + dfCenters.reset_index()['index'].astype(int).add(1).astype(str)

            dfDeparture = pd.DataFrame([[departure_lon, departure_lat,'Departure']],columns=['lon','lat','cluster'])
            dfCenters = pd.concat([dfDeparture,dfCenters], ignore_index=True)

            #Pick random number of clusters
            #-------------------------------------------------------------
            selected_clusters = ['Departure']
            nbr_clusters_to_visit = cruise_stages #np.random.randint(low = min_cruise_stages, high = max_cruise_stages)
            selected_clusters.extend(dfCenters.sample(nbr_clusters_to_visit).cluster.tolist())

            #Generate the cruise's route
            #-------------------------------------------------------------
            chosen_route = []
            for idx, c in enumerate(selected_clusters[:-1]):
                origin = (dfCenters.loc[dfCenters.cluster == c, 'lat'].values[0], dfCenters.loc[dfCenters.cluster == c, 'lon'].values[0])
                destination = (dfCenters.loc[dfCenters.cluster == selected_clusters[idx+1], 'lat'].values[0], dfCenters.loc[dfCenters.cluster == selected_clusters[idx+1], 'lon'].values[0])
                partial_route = compute_maritime_route(origin, destination)
                chosen_route.append(partial_route)
            complete_route = pd.concat(chosen_route, ignore_index=True)

            #Adapt line for problematic points (i.e. going out of the screen)
            #waypoints is a pandas df with columns lon and lat in degrees ranging from -180 to 180
            #-------------------------------------------------------------
            waypoints = complete_route.copy()
            waypoints = waypoints.rename(columns = {'latitude':'lat','longitude':'lon'}) 
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
            activities_color_map = {'Departure':'yellow'}
            activities_color_map.update(activities_mapping)
            activities_clusters = (selected_clusters).copy()
            dfActivities_locations = dfCenters.query('cluster.isin(@activities_clusters)').copy()
            activities_types = st.session_state['_type_activities_']
            dfActivities_locations['activity'] = ""
            for idx, row in dfActivities_locations.iterrows():
                dfActivities_locations.loc[idx,'activity'] = random.choice(activities_types)
            dfActivities_locations.loc[0,'activity'] = 'Departure'
            
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


            #Export Cruise / History
            #-------------------------------------------------------------
            save_cruise = False
            if c5.button('💾Save', use_container_width=True):
               save_cruise = True 
            else:
                st.session_state['_cruise_bookmarks_']['temp_save'] = dict()
                st.session_state['_cruise_bookmarks_']['temp_save']['departure_country'] = st.session_state['_selected_country_']
                st.session_state['_cruise_bookmarks_']['temp_save']['departure_port'] = departure_port
                st.session_state['_cruise_bookmarks_']['temp_save']['period_start'] = st.session_state['_start_year_']
                st.session_state['_cruise_bookmarks_']['temp_save']['period_end'] = st.session_state['_end_year_']
                st.session_state['_cruise_bookmarks_']['temp_save']['cruise_stages'] = st.session_state['_number_activities_']
                st.session_state['_cruise_bookmarks_']['temp_save']['waypoints'] = waypoints
                st.session_state['_cruise_bookmarks_']['temp_save']['dfActivities_locations'] = dfActivities_locations
            if save_cruise:
                switch_page('Cruise save')
            if c5.button('🔖Bookmarks', use_container_width=True):
                switch_page('Bookmarks')