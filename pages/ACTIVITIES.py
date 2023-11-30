import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px


from backend.Sharks_streamlit_utils_v1 import get_session_state, extract_popular_activities
from streamlit_plotly_events import plotly_events

var_list = get_session_state(['transformed_data/sharks','transformed_data/activities_words'])
sharks, activities = var_list[0], var_list[1]

st.title('Activities Explorer')
st.divider()
c1, c2, c3 = st.columns([10,2,30])

popular_activities = extract_popular_activities(activities)

def build_bar_chart(popular_activities):
    fig = px.bar(popular_activities.sort_values('occurence',ascending = False),x = 'Activity',y = 'occurence', title = 'Most popular activities leading to attacks',
                color= 'Activity', color_discrete_sequence=px.colors.qualitative.Set3, height = 1000)
    fig.update_layout(showlegend=False) # Remove legend
    #fig.update_xaxes(tickangle=90)

    return fig

def build_map(popular_activities,sharks):
    sharks['Activity_term'] = "other"
    sharks.Activity = (sharks.Activity.str.lower().str.replace("(?i)[^a-z ]",'', regex= True).fillna('-'))
    sharks['Activity_list'] = sharks.Activity.str.split(' ')
    for word in popular_activities.Activity.unique().tolist():
        #sharks.loc[sharks.Activity.str.contains(word),'Activity_term'] = word
        sharks.loc[[word in x for x in sharks.Activity_list],'Activity_term'] = word #note that by doing that, some records are assigned 1 activity although there are multiple !
    #sharks = pd.merge(sharks, popular_activities.rename(columns = {'Activity':'Activity_term'}).filter(['Activity_term','occurence']), on = 'Activity_term',how = 'left')

    sharks['occurence'] = sharks.groupby('Activity_term')['latitude'].transform('count')

    fig = px.scatter_geo(pd.concat([sharks.query('Activity_term != "other"').sort_values('occurence', ascending = False),sharks.query('Activity_term == "other"')], ignore_index=True),
                        color = 'Activity_term', lat = 'latitude',lon = 'longitude',height = 1000,
                        color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(margin=dict(l=0,r=0,b=0,t=0),paper_bgcolor="rgba(0, 0, 0, 0)") # Remove margin and make remaining background transparent
    fig.update_layout(legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="right",x=0.97))
    fig.update_geos(showcoastlines=True, coastlinecolor = '#afe3e0',showland=True, landcolor='#76b0a6',showocean=True, oceancolor= '#50545c')
    fig.update_traces(marker=dict(line=dict(width=1, color="Black")))

    return fig

#Successful Activities
fig = build_bar_chart(popular_activities)
#c1.plotly_chart(fig, use_container_width= True)
with c1:
    map_selection = plotly_events(fig, select_event=True, key=f"_country_selector_")

#Activity mapping
fig = build_map(popular_activities,sharks)
c3.plotly_chart(fig, use_container_width= True)