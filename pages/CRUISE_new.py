import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from backend.Sharks_utils_v1 import define_clusters, clean_clusters_centerpoints, compute_maritime_route
from backend.Sharks_streamlit_utils_v1 import get_session_state

cluster_distance = 10 #10 #km : maximum_distance_within_cluster
cluster_minsize = 5 #5 #minimum_number_attacks_within_cluster
min_cruise_stages = 2
max_cruise_stages = 4
dfPorts = pd.read_csv('input_data/ports.csv').filter(['Main Port Name','Country Code','Latitude','Longitude']).rename(columns = {'Main Port Name':'Port','Country Code':'Country'})

var_list = get_session_state(['transformed_data/sharks'])
sharks = var_list[0]
sharks['coordinates'] = sharks.filter(['latitude', 'longitude']).values.tolist()

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space

def render_mapbox_cruise(sharks_selection):
    style_dict = {'map':"open-street-map",'white':"carto-positron",'dark':"carto-darkmatter",'terrain':"stamen-terrain",'bw':"stamen-toner",'realistic':"white-bg"}
    mapboxstyle = 'map' #['map','white','dark','terrain','bw','realistic'])

    fig = px.scatter_mapbox(sharks_selection.dropna(subset = 'coordinates'),
                    lat='latitude',
                    lon='longitude',
                    #projection = 'natural earth',
                    #color = 'cluster',
                    title = f'Attacks location colored by cluster',
                    #hover_name = 'cluster',
                    #hover_data= {'cluster':False, 'cluster_content':True, 'latitude':':.2f','longitude':':.2f'},
                    height= 1200,
                    #template= 'plotly_dark',
                    zoom = 1.6
                    )

    if style_dict[mapboxstyle] == "white-bg":

        fig.update_layout(mapbox_layers=[{"below": 'traces',
                                            "sourcetype": "raster",
                                            "sourceattribution": "United States Geological Survey",
                                            "source": [
                                                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]}])

    fig.update_layout(mapbox_style=style_dict[mapboxstyle],mapbox_center= {'lat':0,'lon':0})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    fig.update_traces(marker=dict(size=12,),
                    selector=dict(mode='markers'))
    
    return fig

if '_selected_country_' not in st.session_state:
    st.info('Please select a departure country in the Home page')
else:
    if st.session_state['_selected_country_'] == 0:
        st.info('Please select a departure country in the Home page')
    else:
        st.write(st.session_state)
        departure_country = st.session_state['_selected_country_']
        period_start = st.session_state['_start_year_']
        period_end = st.session_state['_end_year_']
        if dfPorts.query('Country == @departure_country').empty:
            st.warning("Please select another country. This one doesn't have any harbor we can start the cruise with.")
        else:

            #Select random Harbor among available within departure country
            #-------------------------------------------------------------
            departure_port = dfPorts.query('Country == @departure_country').sample(1)
            departure_lat = departure_port.Latitude.values[0]
            departure_lon = departure_port.Longitude.values[0]
            st.success(f'Departure Harbor : **{departure_port.Port.values[0]}** ({departure_country})')

            #Filter out data not in study period & extract coordinates for clustering analysis
            #-------------------------------------------------------------
            sharks_selection = sharks.query("date >= @period_start").query("date <= @period_end").copy()
            selected_attacks_coordinates = sharks_selection.filter(['latitude', 'longitude']).dropna().values

            #Generate clusters & their center point
            #-------------------------------------------------------------
            dfcluster, clusters, results_print = define_clusters(selected_attacks_coordinates, max_km_btwn_points_in_cluster=cluster_distance, min_cluster_size=cluster_minsize)

            with st.sidebar:
                st.markdown('Dropped entries without coordinates: {}'.format(sharks_selection.filter(['latitude', 'longitude']).isna().any(axis=1).sum()))
                for i in results_print:
                    st.markdown(i)

            dfCenters = clean_clusters_centerpoints(clusters)
            dfCenters['cluster'] = "Cluster n°" + dfCenters.reset_index()['index'].astype(int).add(1).astype(str)

            dfDeparture = pd.DataFrame([[departure_lon, departure_lat,'Departure']],columns=['lon','lat','cluster'])
            dfCenters = pd.concat([dfDeparture,dfCenters], ignore_index=True)

            #Pick random number of clusters
            #-------------------------------------------------------------
            selected_clusters = ['Departure']
            nbr_clusters_to_visit = np.random.randint(low = min_cruise_stages, high = max_cruise_stages)
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
            
            #Cruise
            #-------------------------------------------------------------
            fig.add_trace(go.Scattermapbox(lat = waypoints.lat,
                                                lon = lons,
                                                mode = 'lines',
                                                line = dict(color = 'black')))
            
            #Activities
            #-------------------------------------------------------------

            #History
            #-------------------------------------------------------------

            #Export Cruise
            #-------------------------------------------------------------


            #Render the map & generate
            st.plotly_chart(fig, use_container_width= True)

            st.sidebar.button('Generate another Cruise', type = 'primary')