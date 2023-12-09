import pandas as pd
import streamlit as st
import plotly.express as px
from st_pages import Page, show_pages, add_page_title, hide_pages, Section
from streamlit_plotly_events import plotly_events

#activities_mapping = {'surfing': 'rgb(141,211,199)', 'swimming': 'rgb(255,255,179)', 'fishing': 'rgb(190,186,218)', 'diving': 'rgb(251,128,114)', 'spearfishing': 'rgb(128,177,211)', 'bathing': 'rgb(253,180,98)', 'wading': 'rgb(179,222,105)', 'scuba': 'rgb(252,205,229)', 'snorkeling': 'rgb(217,217,217)', 'kayaking': 'rgb(188,128,189)'}
activities_mapping = {'surfing': 'rgb(255,255,179)', 'swimming': 'rgb(190,186,218)', 'fishing': 'rgb(251,128,114)', 'diving': 'rgb(128,177,211)', 'spearfishing': 'rgb(253,180,98)', 'bathing': 'rgb(179,222,105)', 'wading': 'rgb(252,205,229)', 'scuba': 'rgb(217,217,217)', 'snorkeling': 'rgb(188,128,189)', 'kayaking': 'rgb(204,235,197)'}

def get_session_state(var_list:list):
    var_data_list = []
    for var in var_list:
        if var not in st.session_state:
            var_data = pd.read_parquet(f'{var}.parquet')
            st.session_state[var] = var_data
        else:
            var_data = st.session_state[var]

        var_data_list.append(var_data)

    return var_data_list

def initialize_state_activities():
    """Initializes all Session State variables"""

    for session_name in ['_selected_activity_']:
        if session_name not in st.session_state:
            st.session_state[session_name] = 0

def initialize_state_filters():
    """Initializes all Session State variables"""

    for session_name in ['_start_year_','_end_year_','_number_activities_','_type_activities_']:
        if session_name not in st.session_state:
            st.session_state[session_name] = 0

def initialize_state_saves():
    """Initializes all Session State variables"""

    for session_name in ['_cruise_bookmarks_',]:
        if session_name not in st.session_state:
            st.session_state[session_name] = {}

def build_activities_chart(popular_activities, activities_mapping):
    fig = px.bar(popular_activities.sort_values('occurence',ascending = False),x = 'Activity',y = 'occurence', title = 'Most popular activities leading to attacks',
                color= 'Activity', color_discrete_sequence=popular_activities.assign(color = popular_activities.Activity.map(activities_mapping)).sort_values('occurence',ascending = False).color)#px.colors.qualitative.Set3)
    fig.update_layout(showlegend=False) # Remove legend
    fig.update_layout(paper_bgcolor="rgba(0, 0, 0, 0)",
                      plot_bgcolor='rgba(0,0,0,0)',
                      font_color = "white"
                      )
    fig.update_yaxes(gridcolor='Grey') #showgrid = False
    #fig.update_xaxes(tickangle=90)

    return fig

def build_activities_map(popular_activities,sharks, unselected_color, show_unselected):
    #Construct df
    sharks['Activity_term'] = "other"
    sharks.Activity = (sharks.Activity.str.lower().str.replace("(?i)[^a-z ]",'', regex= True).fillna('-'))
    sharks['Activity_list'] = sharks.Activity.str.split(' ')
    for word in popular_activities.Activity.unique().tolist():
        #sharks.loc[sharks.Activity.str.contains(word),'Activity_term'] = word
        sharks.loc[[word in x for x in sharks.Activity_list],'Activity_term'] = word #note that by doing that, some records are assigned 1 activity although there are multiple !
    sharks['occurence'] = sharks.groupby('Activity_term')['latitude'].transform('count')

    #Map the color for the points
    sharks = pd.merge(sharks, popular_activities.rename(columns = {'Activity':'Activity_term'}).filter(['Activity_term','color']), on = 'Activity_term',how = 'left')
    sharks.loc[sharks.color == unselected_color,'Activity_term'] = "other"
    
    #Construct plot
    fig = px.scatter_geo(pd.concat([sharks.query('Activity_term != "other"').sort_values('occurence', ascending = False),sharks.query('Activity_term == "other"')], ignore_index=True),
                        color = 'Activity_term', lat = 'latitude',lon = 'longitude',#height = 1000,
                        color_discrete_sequence= pd.concat([sharks.query('Activity_term != "other"').sort_values('occurence', ascending = False),sharks.query('Activity_term == "other"')], ignore_index=True).color.unique().tolist())
                        #popular_activities.sort_values(['color','occurence']).color.tolist()) #sorting to ensure good color association
    
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0),paper_bgcolor="rgba(0, 0, 0, 0)") # Remove margin and make remaining background transparent
    #fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.1,xanchor="right",x=1))
    fig.update_geos(showcoastlines=True, coastlinecolor = '#afe3e0',showland=True, landcolor='#76b0a6',showocean=True, oceancolor= '#50545c') #map color
    fig.update_traces(marker=dict(size = 10,line=dict(width=2, color="Black"))) #marker border
    fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)')) #Color when zoom out of map

    if show_unselected:
        fig.update_traces(opacity = 0.3, selector = ({'name':'other'})) #decrease opacity for "other" markers
    else:
        fig.update_traces(opacity = 0, selector = ({'name':'other'})) #decrease opacity for "other" markers

    return fig

def render_activities_chart(df, activities_mapping):
    #Select a country (only if no country yet selected)
    #---------------------------------------------------
    fig = build_activities_chart(df, activities_mapping)
    bar_selection = plotly_events(fig, select_event=True, key=f"_activity_selector_")
    if bar_selection != []:
        st.session_state['_selected_activity_'] = bar_selection[0]['x']
        need_update = True
    else:
        need_update = False

    return need_update

def render_mapbox_cruise(sharks_selection):
    style_dict = {'map':"open-street-map",'white':"carto-positron",'dark':"carto-darkmatter",'terrain':"stamen-terrain",'bw':"stamen-toner",'realistic':"white-bg"}
    mapboxstyle = 'white' #['map','white','dark','terrain','bw','realistic'])

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
                    zoom = 1.45
                    )

    if style_dict[mapboxstyle] == "white-bg":

        fig.update_layout(mapbox_layers=[{"below": 'traces',
                                            "sourcetype": "raster",
                                            "sourceattribution": "United States Geological Survey",
                                            "source": [
                                                "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]}])

    fig.update_layout(mapbox_style=style_dict[mapboxstyle],mapbox_center= {'lat':0,'lon':0})
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    fig.update_traces(marker=dict(size=7,),
                    selector=dict(mode='markers'))
    
    return fig

def order_and_hide_pages(hidden_pages = ["Cruise visualization","Homepage","Cruise save"]):
    add_page_title()
    show_pages(
        [
            Page("Sharks_streamlit_v3.py", "Homepage", "📈"),

            Section('Cruise','⛵'),
            Page("pages/HOME.py", "Generate", "⚙️"),
            Page("pages/CRUISE_new.py", "Cruise visualization", "🗺️"),
            Page("pages/Cruise_save.py", "Cruise save", "💾"),
            Page("pages/Cruise_bookmarks.py", "Bookmarks", "🔖"),

            Page("pages/PRACTICAL.py", "Data explorer", "🔎", in_section=False),

            Page("pages/TRACKING.py", "Business tracker", "📈", in_section=False),  
        ]
    )

    hide_pages(hidden_pages)
