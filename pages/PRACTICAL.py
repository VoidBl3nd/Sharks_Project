import pandas as pd
import streamlit as st
import plotly.express as px

from backend.Sharks_streamlit_utils_v1 import get_session_state, extract_popular_activities, build_activities_map, render_activities_chart, initialize_state_activities

var_list = get_session_state(['transformed_data/sharks', 'transformed_data/bodyparts_words', 'transformed_data/activities_words'])
sharks, body_parts, activities = var_list[0], var_list[1], var_list[2]
popular_activities = extract_popular_activities(activities)

#Initialize Streamlit
st.set_page_config(page_title="Sharky cruise builder", layout = "wide", page_icon= '🦈') # must happen before any streamlit code /!\
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True) # remove blank top space

st.title('Historical data information',) # #Practical information about past attacks
st.divider()
c1,c2 = st.columns(2)

#region -> Distribution of attacks over the months (excluding unformatted dates)
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
month_dist = sharks.assign(month = sharks.date.dt.month_name()).groupby(['month']).agg(nbr_attacks = ('month','count'))
fig = px.bar(month_dist , y='nbr_attacks',title = 'Distribution of the number of sharks attacks over the months',
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_xaxes(categoryorder='array', categoryarray= month_order)

c1.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Distribution of attacks over accross the day (excluding unformatted times)
time_dist = sharks.time.groupby(sharks.time).size()
time_dist.index = pd.PeriodIndex("01-01-2001 "+ time_dist.index.astype(str), freq = 'T')
time_dist = time_dist.resample('30T').sum().rename('nbr_attacks').reset_index()
time_dist.time = time_dist.time.dt.strftime('%H:%M')
fig = px.bar(time_dist, x= 'time',y = 'nbr_attacks', title = 'Distribution of the number of sharks attacks accross a day (30 mins interval)',
             color_discrete_sequence=px.colors.qualitative.Set3)

c2.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Distribution of attacks accross genders
sex_dist = sharks.groupby('Sex').Sex.count().rename('nbr_attacks').reset_index()
fig = px.pie(sex_dist, values='nbr_attacks', names='Sex', title = 'Repartition of attacks accross genders',
             color_discrete_sequence=px.colors.qualitative.Set3)
fig.update_traces(hoverinfo='label+percent+value', textinfo='label+percent', textfont_size=20,
                  marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(showlegend=False)
c1.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Popularity of body parts
fig = px.bar(body_parts.drop(body_parts[body_parts.injury_term.isin(['left','right'])].index).sort_values('occurences',ascending = False).head(12),y = 'injury_term',x = 'occurences', orientation = 'h', title = 'Appearance of the different "Body part" terms in the Injury attribute',
             color= 'injury_term', color_discrete_sequence=[px.colors.qualitative.Set3[0]],)
#fig.update_layout(yaxis={'categoryorder':'total ascending'})
fig.update_layout(showlegend=False)
c2.plotly_chart(fig, use_container_width= True)
#endregion

#region -> Popularity & mapping of activities
with st.expander('Interactive activities charts', expanded= True):
    initialize_state_activities()
    c1,c2 = st.columns(2)
    
    with c1:
        render_activities_chart(popular_activities)
        c1a,c1b,c1c = st.columns([1,1,1])

        #May reset activity or use the one selected
        if c1b.button('Reset selection', use_container_width= True):
            st.session_state['_selected_activity_'] = 0
        selected_activity = [st.session_state['_selected_activity_']]

        #Display chosen activity
        if selected_activity == [0]:
            c1a.info(f"You can select an activity to filter the map")
        else:
            c1a.success(f"Selected activity : **{selected_activity[0].capitalize()}**")

        #Toggle
        show_unselected = c1c.toggle('Show unselected data', value= True)

    with c2:
        #Set unselected activities to grey opacity
        unselected_color = "rgba(41, 40, 39,50)"
        popular_activities['color'] = px.colors.qualitative.Set3[:len(popular_activities)]
        if selected_activity != [0]:
            popular_activities.loc[~popular_activities.Activity.isin(selected_activity),'color'] = unselected_color

        fig = build_activities_map(popular_activities,sharks, unselected_color, show_unselected)
        st.plotly_chart(fig, use_container_width= True)
#endregion