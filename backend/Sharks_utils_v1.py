import numpy as np
import pandas as pd
import plotly.express as px

from sklearn.cluster import DBSCAN 
from geopy.distance import great_circle #pip install geopy
from shapely.geometry import MultiPoint #pip install shapely
from scgraph.geographs.marnet import marnet_geograph #pip install scgraph

#region -> MARITIME ROUTE
def compute_maritime_route(origin:tuple, destination:tuple) -> pd.DataFrame:
    """
    Provided a origin and a destination, will return a path composed of multiple points 
    
    """    
    # Compute shorthest path 
    path_dict = marnet_geograph.get_shortest_path(origin_node={"latitude": origin[0],
                                                               "longitude": origin[1]}, 
                                                  destination_node={"latitude": destination[0],
                                                                    "longitude": destination[1]})
    df = pd.DataFrame(path_dict['coordinate_path'])
    return df

def plot_maritime_route(df_Coordinates_sequence:pd.DataFrame):
    fig = px.line_geo(df_Coordinates_sequence, lat='latitude',lon='longitude')
    return fig
#endregion

#region -> CLUSTERS
def define_clusters(coordinates:np.array, max_km_btwn_points_in_cluster:int|float = 50, min_cluster_size:int = 10) -> tuple[pd.DataFrame, pd.Series]:
    #Clustering algorithm
    kms_per_radian = 6371.0088
    epsilon = max_km_btwn_points_in_cluster / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=min_cluster_size, algorithm='ball_tree', metric='haversine').fit(np.radians(coordinates))

    #Extract results of the clustering
    cluster_labels = db.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([coordinates[cluster_labels == n] for n in range(num_clusters)])

    #Print results of the clustering
    results_print = []
    results_print.append('Number of clusters: {}'.format(num_clusters - 1))
    results_print.append('Total input points: {}'.format(len(coordinates)))
    results_print.append('Clustered points: {}'.format(pd.Series(cluster_labels).value_counts().reset_index().query('index != -1')[0].sum()))
    results_print.append('Noise points: {}'.format(pd.Series(cluster_labels).value_counts().reset_index().query('index == -1')[0].values[0]))
    results_print.append('Cluster content: {}'.format(pd.Series(cluster_labels).value_counts().reset_index(name = 'population').rename(columns = {'index':'cluster'}).query('cluster != -1').sort_values('cluster').population.to_list()))

    #Store result in dataframe
    dfcluster = pd.DataFrame(clusters).reset_index().rename(columns = {0:'coordinates', 'index':'cluster'}).explode('coordinates').reset_index(drop = True).dropna()
    dfcluster[['latitude','longitude']] = pd.DataFrame(dfcluster['coordinates'].tolist(), index= dfcluster.index)

    return dfcluster, clusters, results_print

def get_clusters_centerpoints(cluster):
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    return tuple(centermost_point)

def clean_clusters_centerpoints(clusters):
    clusters = clusters[clusters.str.len() != 0]
    centermost_points = clusters.map(get_clusters_centerpoints)
    lats, lons = zip(*centermost_points)
    dfPoints = pd.DataFrame({'lon':lons, 'lat':lats})
    return dfPoints
#endregion