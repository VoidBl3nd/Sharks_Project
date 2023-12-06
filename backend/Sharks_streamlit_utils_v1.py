import pandas as pd
import streamlit as st
import plotly.express as px
from st_pages import Page, show_pages, add_page_title, hide_pages, Section
from streamlit_plotly_events import plotly_events

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

def extract_popular_activities(activities):
    #popular_activites = activities.head(30).copy().extensions.explode().reset_index()
    #popular_activites[['Activity','occurence']] = popular_activites.extensions.str.split('(', expand = True)
    #popular_activites.occurence = popular_activites.occurence.str.replace(')', '', regex = True)
    #popular_activites = popular_activites.dropna().astype({'occurence':int})
    #popular_activites = (popular_activites
    #                    .drop('index', axis = 1)
    #                    .drop_duplicates()
    #                    .sort_values('occurence', ascending = False)
    #                    .drop(popular_activites[popular_activites.Activity.isin(['boardin','sharks','surface','walking','shupwreck'])].index)
    #                    .head(11)
    #                    .copy()
    #                    .reset_index(drop = True))
    popular_activites = (activities.drop(activities[activities.activity_term.isin(['water','shark','from','standing','boarding','boat','body','fell','free','with','into','overboard','capsized','sharks','boogie','fish','ship','ship','after','surf','floating','treading','board','overboard'])].index)
                        .head(10)
                        .reset_index()
                        .rename(columns = {'activity_term':'Activity','occurences':'occurence'})
                        .filter(['Activity','occurence']))
    return popular_activites

def initialize_state_activities():
    """Initializes all Session State variables"""

    for session_name in ['_selected_activity_']:
        if session_name not in st.session_state:
            st.session_state[session_name] = 0

def build_activities_chart(popular_activities):
    fig = px.bar(popular_activities.sort_values('occurence',ascending = False),x = 'Activity',y = 'occurence', title = 'Most popular activities leading to attacks',
                color= 'Activity', color_discrete_sequence=px.colors.qualitative.Set3)
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
                        color_discrete_sequence=popular_activities.sort_values(['color','occurence']).color.tolist()) #sorting to ensure good color association
    
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0),paper_bgcolor="rgba(0, 0, 0, 0)") # Remove margin and make remaining background transparent
    #fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.1,xanchor="right",x=1))
    fig.update_geos(showcoastlines=True, coastlinecolor = '#afe3e0',showland=True, landcolor='#76b0a6',showocean=True, oceancolor= '#50545c') #map color
    fig.update_traces(marker=dict(line=dict(width=1, color="Black"))) #marker border
    fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)')) #Color when zoom out of map

    if show_unselected:
        fig.update_traces(opacity = 0.3, selector = ({'name':'other'})) #decrease opacity for "other" markers
    else:
        fig.update_traces(opacity = 0, selector = ({'name':'other'})) #decrease opacity for "other" markers

    return fig

def render_activities_chart(df):
    #Select a country (only if no country yet selected)
    #---------------------------------------------------
    fig = build_activities_chart(df)
    bar_selection = plotly_events(fig, select_event=True, key=f"_activity_selector_")
    if bar_selection != []:
        st.session_state['_selected_activity_'] = bar_selection[0]['x']
        need_update = True
    else:
        need_update = False

    return need_update

def initialize_state_filters():
    """Initializes all Session State variables"""

    for session_name in ['_start_year_','_end_year_','_number_activities_','_type_activities_']:
        if session_name not in st.session_state:
            st.session_state[session_name] = 0

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

def initialize_state_saves():
    """Initializes all Session State variables"""

    for session_name in ['_cruise_bookmarks_',]:
        if session_name not in st.session_state:
            st.session_state[session_name] = {}