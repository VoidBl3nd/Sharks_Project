import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import date


from backend.Sharks_streamlit_utils_v1 import get_session_state
from backend.Sharks_utils_v1 import compute_maritime_route, define_clusters, clean_clusters_centerpoints

#Filter year
#Filter area
#Filter hour
#Set min attack number
#Set max km separation
#Display information : sample
#Generate cluster

#Pick Cluster
#Generate Path
#Display information : distance, stop steps

sharks = get_session_state(['transformed_data/sharks'])[0]
sharks = sharks[[col for col in sharks.columns if col not in ['coordinates']]]

with st.sidebar:
    st.header('Sharky Cruise Builder')
    style_dict = {'map':"open-street-map",'white':"carto-positron",'dark':"carto-darkmatter",'terrain':"stamen-terrain",'bw':"stamen-toner",'realistic':"white-bg"}
    mapboxstyle = st.selectbox('Map style', options = ['map','white','dark','terrain','bw','realistic'])
    st.divider()

    st.subheader('Sampling Parameters')
    sample_period = st.date_input('Sample period',
                                    value = (date(2000,1,1), sharks.date.max().date()),
                                    min_value= sharks.date.min().date(),
                                    max_value= sharks.date.max().date(),
                                    format = 'DD/MM/YYYY')
    st.divider()

    st.subheader('Clustering Parameters')
    cluster_distance = st.number_input('Maximum distance within a cluster (km)',
                                       min_value= 1,
                                       value= 50)
    cluster_minsize = st.number_input('Minimum number of elements within a cluster',
                                      min_value= 1,
                                      value = 10,
                                      format = '%i')
    
    st.button('Generate clusters', type="primary", use_container_width= True)

if len(sample_period) <= 1:
    sample_period = (date(2000,1,1), sharks.date.max().date())
######################################

sharks_selection = (sharks.query('date >= @sample_period[0]')
                        .query('date <= @sample_period[1]')
                ).copy()

######################################
selected_attacks_coordinates = sharks_selection.filter(['latitude', 'longitude']).dropna().values
dfcluster, clusters, results_print = define_clusters(selected_attacks_coordinates, max_km_btwn_points_in_cluster=cluster_distance, min_cluster_size=cluster_minsize)

with st.sidebar:
    st.markdown('Dropped entries without coordinates: {}'.format(sharks_selection.filter(['latitude', 'longitude']).isna().any(axis=1).sum()))
    for i in results_print:
        st.markdown(i)

######################################

sharks_clustered = pd.merge(sharks_selection, dfcluster.drop_duplicates(subset=['latitude','longitude']), on = ['latitude','longitude'],how = 'left' )
sharks_clustered['cluster_content'] = sharks_clustered.groupby(['cluster'], dropna = False).cluster.transform('count')
sharks_clustered['cluster'] = "Cluster n°" + sharks_clustered['cluster'].replace(np.NaN,-1).astype(int).add(1).astype(str)

sharks_clustered.cluster = sharks_clustered.cluster.astype(str)
fig = px.scatter_mapbox(sharks_clustered.dropna(subset = 'coordinates'),
                    lat='latitude',
                    lon='longitude',
                    #projection = 'natural earth',
                    color = 'cluster',
                    title = f'Attacks location colored by cluster',
                    hover_name = 'cluster',
                    hover_data= {'cluster':False, 'cluster_content':True, 'latitude':':.2f','longitude':':.2f'},
                    height= 1200,
                    #template= 'plotly_dark',
                    zoom = 2
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

#st.plotly_chart(fig, use_container_width= True)


#####################################
dfCenters = clean_clusters_centerpoints(clusters)
dfCenters['cluster'] = "Cluster n°" + dfCenters.reset_index()['index'].astype(int).add(1).astype(str)

with st.sidebar:
    st.divider()
    st.subheader('Cruise Parameters')
    selected_clusters = st.multiselect('Clusters to visit', sharks_clustered.assign(cl = sharks_clustered.cluster.str.replace('Cluster n°','').astype(int)).query('cluster != "Cluster n°0"').sort_values('cl').cluster.unique())

chosen_route = []
for idx, c in enumerate(selected_clusters[:-1]):
    #print(c)
    origin = (dfCenters.loc[dfCenters.cluster == c, 'lat'].values[0], dfCenters.loc[dfCenters.cluster == c, 'lon'].values[0])
    destination = (dfCenters.loc[dfCenters.cluster == selected_clusters[idx+1], 'lat'].values[0], dfCenters.loc[dfCenters.cluster == selected_clusters[idx+1], 'lon'].values[0])
    partial_route = compute_maritime_route(origin, destination)

    #print(len(partial_route))
    chosen_route.append(partial_route)

if len(chosen_route) > 0:
    complete_route = pd.concat(chosen_route, ignore_index=True)


    #Adapt line for problematic points
    #waypoints is a pandas df with columns lon and lat in degrees ranging from -180 to 180
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

    fig.add_trace(go.Scattermapbox(lat = waypoints.lat,#complete_route.latitude,
                                    lon = lons,#complete_route.longitude,
                                    #projection_type  = 'natural earth',
                                    mode = 'lines',
                                    line = dict(color = 'black'))) #width = 4
    

#fig.update_traces(cluster=dict(enabled=True))

st.plotly_chart(fig, use_container_width= True)